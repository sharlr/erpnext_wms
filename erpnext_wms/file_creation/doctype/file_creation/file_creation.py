from frappe.model.document import Document


class FileCreation(Document):
	def on_submit(self):
		self.db_set("status", "Submitted")

	def on_cancel(self):
		self.db_set("status", "Draft")
