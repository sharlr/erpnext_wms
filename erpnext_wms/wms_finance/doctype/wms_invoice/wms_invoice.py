import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_link_to_form


# Frappe resolves the controller as doctype.replace(" ", ""), so "WMS Invoice"
# must be WMSInvoice -- WmsInvoice is silently ignored and the doctype falls
# back to the plain Document class.
class WMSInvoice(Document):
	def validate(self):
		# customer / company / file_type arrive via fetch_from, applied by
		# _validate_links() before this runs
		self.load_payment_vouchers()
		self.calculate_totals()

	def load_payment_vouchers(self):
		"""Rebuild the payment voucher table from the linked file.

		The table is cleared first -- the previous implementation appended on
		every on_change, so a document duplicated its own payment rows on each
		save.
		"""
		self.set("aggregated_payments", [])

		if not self.file_creation:
			return

		vouchers = frappe.get_all(
			"Payment Voucher",
			filters={"file_creation": self.file_creation, "docstatus": 1},
			fields=["name", "payment_date", "amount"],
			order_by="payment_date asc",
		)

		for voucher in vouchers:
			self.append(
				"aggregated_payments",
				{
					"payment_voucher": voucher.name,
					"payment_date": voucher.payment_date,
					"payment_amount": voucher.amount,
				},
			)

	def calculate_totals(self):
		payment_total = sum(flt(row.payment_amount) for row in self.aggregated_payments)

		service_total = 0.0
		for row in self.invoice_items:
			row.amount = flt(row.quantity) * flt(row.rate)
			service_total += flt(row.amount)

		self.total_amount = payment_total + service_total
		self.balance = flt(self.total_amount) - flt(self.paid_amount)

	def before_submit(self):
		if flt(self.total_amount) <= 0:
			frappe.throw(_("Cannot submit an invoice with a zero total"))

		for row in self.invoice_items:
			if flt(row.amount) and not row.income_account:
				frappe.throw(
					_("Row {0}: Income Account is required to post to the ledger").format(row.idx)
				)

	def on_submit(self):
		self.post_to_general_ledger()

	def on_cancel(self):
		self.ignore_linked_doctypes = ("Journal Entry", "GL Entry")
		self.cancel_journal_entry()

	def post_to_general_ledger(self):
		"""Book the receivable and the service income."""
		cost_center = frappe.get_cached_value("Company", self.company, "cost_center")

		journal_entry = frappe.new_doc("Journal Entry")
		journal_entry.voucher_type = "Journal Entry"
		journal_entry.company = self.company
		journal_entry.posting_date = self.invoice_date
		journal_entry.user_remark = _("WMS Invoice {0}").format(self.name)

		for item in self.invoice_items:
			if not flt(item.amount):
				continue

			journal_entry.append(
				"accounts",
				{
					"account": item.income_account,
					"credit_in_account_currency": flt(item.amount),
					"cost_center": cost_center,
				},
			)

		journal_entry.append(
			"accounts",
			{
				"account": self.receivable_account,
				"debit_in_account_currency": flt(self.total_amount),
				"party_type": "Customer",
				"party": self.customer,
				"cost_center": cost_center,
			},
		)

		# aggregated payment vouchers carry no income account of their own, so
		# balance them against the company's default receivable contra account
		difference = flt(self.total_amount) - sum(
			flt(item.amount) for item in self.invoice_items
		)
		if difference:
			journal_entry.append(
				"accounts",
				{
					"account": self.get_default_income_account(),
					"credit_in_account_currency": difference,
					"cost_center": cost_center,
				},
			)

		journal_entry.insert(ignore_permissions=True)
		journal_entry.submit()

		# db_set, not save(): self is already submitted at this point
		self.db_set("journal_entry", journal_entry.name)

		frappe.msgprint(
			_("Posted to {0}").format(get_link_to_form("Journal Entry", journal_entry.name)),
			indicator="green",
			alert=True,
		)

	def get_default_income_account(self):
		account = frappe.get_cached_value("Company", self.company, "default_income_account")
		if not account:
			frappe.throw(
				_("Set the Default Income Account on Company {0} first").format(self.company)
			)

		return account

	def cancel_journal_entry(self):
		if not self.journal_entry:
			return

		if not frappe.db.exists("Journal Entry", self.journal_entry):
			return

		journal_entry = frappe.get_doc("Journal Entry", self.journal_entry)
		if journal_entry.docstatus == 1:
			journal_entry.cancel()

		self.db_set("journal_entry", None)
