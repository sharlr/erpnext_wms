from frappe.model.document import Document

class ExportFile(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_required_fields()
    
    def calculate_totals(self):
        total_qty = 0
        total_weight = 0
        total_value = 0
        
        for item in self.export_items:
            total_qty += item.quantity or 0
            total_weight += (item.weight or 0) * (item.quantity or 0)
            total_value += (item.rate or 0) * (item.quantity or 0)
        
        self.total_quantity = total_qty
        self.total_weight = total_weight
        self.total_value = total_value
    
    def validate_required_fields(self):
        if not self.customer:
            raise ValueError("Customer is required")
        if not self.export_items:
            raise ValueError("Add at least one item")

def on_submit_export_file(doc, event):
    doc.status = "Submitted"
    doc.save()
