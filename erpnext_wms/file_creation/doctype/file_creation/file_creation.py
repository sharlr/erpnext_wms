import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname

# Import files and export files get their own series so the file number itself
# says which kind of file it is.
NAMING_SERIES = {
	"Import": "IM-.YYYY.-.####",
	"Export": "EX-.YYYY.-.####",
}


class FileCreation(Document):
	def autoname(self):
		"""Name from the file type.

		naming.set_new_name() calls this before falling back to meta.autoname,
		so the doctype carries no autoname of its own.
		"""
		series = NAMING_SERIES.get(self.file_type)
		if not series:
			frappe.throw(_("Select a File Type before saving"))

		self.name = make_autoname(series, doc=self)

	def on_submit(self):
		self.db_set("status", "Submitted")

	def on_cancel(self):
		self.db_set("status", "Draft")
