import frappe
from frappe.model.document import Document


class WmsInvoice(Document):
    def on_change(self):
        """Load payment vouchers when file is selected"""
        if self.file_creation:
            self.load_payment_vouchers()
            self.update_file_details()

    def load_payment_vouchers(self):
        """Fetch and populate Payment Vouchers for the selected File Creation"""
        payment_vouchers = frappe.get_all(
            "Payment Voucher",
            filters={"file_creation": self.file_creation},
            fields=["name", "payment_date", "amount"]
        )

        self.aggregated_payments = []
        total_payment = 0

        for pv in payment_vouchers:
            self.append("aggregated_payments", {
                "payment_voucher": pv.name,
                "payment_date": pv.payment_date,
                "payment_amount": pv.amount
            })
            total_payment += pv.amount

    def update_file_details(self):
        """Auto-fill customer and file type from File Creation"""
        if self.file_creation:
            file_doc = frappe.get_doc("File Creation", self.file_creation)
            self.customer = file_doc.customer
            self.file_type = file_doc.file_type

    def calculate_totals(self):
        """Calculate total from payment vouchers + custom service items"""
        payment_total = sum([row.payment_amount for row in self.aggregated_payments])
        service_total = sum([row.amount for row in self.invoice_items if hasattr(row, 'amount')])
        self.total_amount = payment_total + service_total
        self.balance = self.total_amount - (self.paid_amount or 0)

    def validate(self):
        """Validate before save"""
        self.calculate_totals()
