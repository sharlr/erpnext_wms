import frappe
from frappe.model.document import Document


class FileCreation(Document):
    def on_submit(self):
        """Create Import File or Export File based on file_type"""
        if self.file_type == "Import":
            self.create_import_file()
        elif self.file_type == "Export":
            self.create_export_file()

    def create_import_file(self):
        """Create Import File from File Creation record"""
        import_file = frappe.get_doc({
            "doctype": "Import File",
            "company": self.company,
            "customer": self.customer,
            "shipping_line": self.shipping_line,
            "awb_bl_number": self.awb_bl_number,
            "status": "Draft"
        })
        import_file.insert(ignore_permissions=True)
        frappe.msgprint(f"Import File {import_file.name} created successfully")

    def create_export_file(self):
        """Create Export File from File Creation record"""
        export_file = frappe.get_doc({
            "doctype": "Export File",
            "company": self.company,
            "customer": self.customer,
            "destination_country": self.destination_country,
            "status": "Draft"
        })
        export_file.insert(ignore_permissions=True)
        frappe.msgprint(f"Export File {export_file.name} created successfully")
