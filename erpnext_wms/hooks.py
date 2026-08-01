app_name = "erpnext_wms"
app_title = "ERPNext Warehouse Management System"
app_publisher = "ERPNext WMS"
app_description = "Complete Warehouse Management System for ERPNext"
app_email = "support@erpnext-wms.com"
app_license = "MIT"
app_version = "1.0.0"

app_include_css = []
app_include_js = []

permission = [
    {
        "doctype": "Import File",
        "name": "WMS User",
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 0,
        "submit": 1,
        "amend": 1
    },
    {
        "doctype": "Export File",
        "name": "WMS User",
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 0,
        "submit": 1,
        "amend": 1
    },
    {
        "doctype": "Stock Adjustment",
        "name": "WMS User",
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 0,
        "submit": 1,
        "amend": 1
    },
    {
        "doctype": "WMS Invoice",
        "name": "WMS Finance",
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 0,
        "submit": 1
    }
]

fixtures = []

scheduler_events = {
    "daily": [
        "erpnext_wms.tasks.generate_storage_charges"
    ]
}

doc_events = {
    "File Creation": {
        "on_submit": "erpnext_wms.doctype.file_creation.file_creation.FileCreation.on_submit"
    },
    "Import File": {
        "on_submit": "erpnext_wms.doctype.import_file.import_file.on_submit_import_file"
    },
    "Export File": {
        "on_submit": "erpnext_wms.doctype.export_file.export_file.on_submit_export_file"
    },
    "Stock Adjustment": {
        "on_submit": "erpnext_wms.doctype.stock_adjustment.stock_adjustment.on_submit_stock_adjustment"
    }
}
