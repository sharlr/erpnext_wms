import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class PaymentVoucher(Document):
	def validate(self):
		if flt(self.amount) <= 0:
			frappe.throw(_("Amount must be greater than zero"))

	def on_submit(self):
		self.db_set("status", "Submitted")

	def on_cancel(self):
		self.db_set("status", "Draft")
