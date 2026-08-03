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

		if not self.awb_bl_number:
			frappe.throw(_("AWB/BL Number is required"))

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

	# status is owned by the "WMS Export File" workflow -- model/workflow.py
	# writes the state straight into the field, so the controller must not
	# fight it with its own db_set()
