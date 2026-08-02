import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class ExportFile(Document):
	def validate(self):
		self.validate_required_fields()
		self.calculate_totals()

	def validate_required_fields(self):
		if not self.customer:
			frappe.throw(_("Customer is required"))

		if not self.export_items:
			frappe.throw(_("Add at least one item"))

	def calculate_totals(self):
		total_qty = 0.0
		total_weight = 0.0
		total_value = 0.0

		for item in self.export_items:
			qty = flt(item.quantity)
			item.amount = qty * flt(item.rate)

			total_qty += qty
			total_weight += flt(item.weight) * qty
			total_value += flt(item.amount)

		self.total_quantity = total_qty
		self.total_weight = total_weight
		self.total_value = total_value

	def on_submit(self):
		# db_set rather than save(): the document is already submitted here, so
		# save() would raise UpdateAfterSubmitError
		self.db_set("status", "Submitted")

	def on_cancel(self):
		self.db_set("status", "Draft")
