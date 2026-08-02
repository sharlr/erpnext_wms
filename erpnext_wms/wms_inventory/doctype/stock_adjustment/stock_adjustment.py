import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_datetime, get_link_to_form


class StockAdjustment(Document):
	def validate(self):
		self.validate_items()
		self.calculate_variances()

	def validate_items(self):
		if not self.warehouse:
			frappe.throw(_("Warehouse is required"))

		if not self.adjustment_items:
			frappe.throw(_("Add at least one item to adjust"))

		for item in self.adjustment_items:
			if flt(item.physical_qty) < 0:
				frappe.throw(_("Row {0}: Physical Qty cannot be negative").format(item.idx))

	def calculate_variances(self):
		"""Fill in the per-row variance and the document total.

		current_qty is read back from the stock ledger rather than trusted from
		the form, so the variance reflects what ERPNext actually holds at the
		moment of validation.
		"""
		total_variance_value = 0.0

		for item in self.adjustment_items:
			item.current_qty = self.get_stock_qty(item.item_code)
			item.variance = flt(item.physical_qty) - flt(item.current_qty)
			item.variance_value = flt(item.variance) * flt(item.rate)
			total_variance_value += flt(item.variance_value)

		self.total_variance_value = total_variance_value

	def get_stock_qty(self, item_code):
		qty = frappe.db.get_value(
			"Bin",
			{"item_code": item_code, "warehouse": self.warehouse},
			"actual_qty",
		)
		return flt(qty)

	def on_submit(self):
		self.make_stock_reconciliation()

	def on_cancel(self):
		self.ignore_linked_doctypes = ("Stock Reconciliation",)
		self.cancel_stock_reconciliation()

	def make_stock_reconciliation(self):
		"""Push the counted quantities into ERPNext's stock ledger.

		A Stock Reconciliation is the right vehicle here: it sets absolute
		quantities rather than deltas, which is what a physical count produces.
		"""
		rows = [item for item in self.adjustment_items if flt(item.variance)]

		if not rows:
			frappe.msgprint(
				_("No quantity differences found, stock ledger left unchanged"),
				indicator="blue",
				alert=True,
			)
			return

		company = frappe.db.get_value("Warehouse", self.warehouse, "company")
		if not company:
			frappe.throw(_("Warehouse {0} is not linked to a Company").format(self.warehouse))

		reconciliation = frappe.new_doc("Stock Reconciliation")
		reconciliation.purpose = "Stock Reconciliation"
		reconciliation.company = company
		reconciliation.set_posting_time = 1
		reconciliation.posting_date = self.adjustment_date
		reconciliation.posting_time = get_datetime().strftime("%H:%M:%S")
		reconciliation.expense_account = self.get_difference_account(company)
		reconciliation.cost_center = frappe.get_cached_value("Company", company, "cost_center")

		for item in rows:
			row = {
				"item_code": item.item_code,
				"warehouse": self.warehouse,
				"qty": flt(item.physical_qty),
			}
			# leaving valuation_rate unset makes ERPNext keep the existing
			# valuation instead of rewriting it to zero
			if flt(item.rate):
				row["valuation_rate"] = flt(item.rate)

			reconciliation.append("items", row)

		reconciliation.insert(ignore_permissions=True)
		reconciliation.submit()

		self.db_set("stock_reconciliation", reconciliation.name)

		frappe.msgprint(
			_("Stock updated via {0}").format(
				get_link_to_form("Stock Reconciliation", reconciliation.name)
			),
			indicator="green",
			alert=True,
		)

	def get_difference_account(self, company):
		account = frappe.get_cached_value("Company", company, "stock_adjustment_account")
		if not account:
			frappe.throw(_("Set the Stock Adjustment Account on Company {0} first").format(company))

		return account

	def cancel_stock_reconciliation(self):
		if not self.stock_reconciliation:
			return

		if not frappe.db.exists("Stock Reconciliation", self.stock_reconciliation):
			return

		reconciliation = frappe.get_doc("Stock Reconciliation", self.stock_reconciliation)
		if reconciliation.docstatus == 1:
			reconciliation.cancel()

		self.db_set("stock_reconciliation", None)
