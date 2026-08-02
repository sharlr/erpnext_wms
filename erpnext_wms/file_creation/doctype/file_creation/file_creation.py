import frappe
from frappe import _
from frappe.model.document import Document

# Naming is driven by the `naming_series` field and autoname "naming_series:",
# not by an autoname() method here. frappe evaluates that from the DocType
# record, so it keeps working even when this controller is not loaded.
NAMING_SERIES = {
	"Import": "IM-.YYYY.-",
	"Export": "EX-.YYYY.-",
}


class FileCreation(Document):
	def before_naming(self):
		"""Server-side mirror of the form script.

		Covers documents created over the API or by other code, where no
		client script runs to set the series.
		"""
		series = NAMING_SERIES.get(self.file_type)
		if not series:
			frappe.throw(_("Select a File Type before saving"))

		self.naming_series = series

	def on_submit(self):
		self.db_set("status", "Submitted")

	def on_cancel(self):
		self.db_set("status", "Draft")
