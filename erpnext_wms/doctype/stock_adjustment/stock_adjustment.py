from frappe.model.document import Document

class StockAdjustment(Document):
    def validate(self):
        self.calculate_variances()
    
    def calculate_variances(self):
        total_variance = 0
        for item in self.adjustment_items:
            variance = (item.physical_qty or 0) - (item.current_qty or 0)
            item.variance = variance
            total_variance += variance * (item.rate or 0)
        
        self.total_variance_value = total_variance

def on_submit_stock_adjustment(doc, event):
    doc.db_set("docstatus", 1)
