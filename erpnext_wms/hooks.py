app_name = "erpnext_wms"
app_title = "ERPNext Warehouse Management System"
app_publisher = "ERPNext WMS"
app_description = "Complete Warehouse Management System for ERPNext"
app_email = "support@erpnext-wms.com"
app_license = "MIT"
app_version = "1.0.0"

# Warehouse, Item, Customer, Company and Journal Entry all come from ERPNext,
# so the bench must refuse to install this app without it.
required_apps = ["erpnext"]

# NOTE: warehouse-visualization.js is deliberately NOT in app_include_js. It
# needs the three.js global and the standalone page's canvas, so the page at
# /assets/erpnext_wms/warehouse-visualization.html loads it directly.

# The doctype JSONs grant permissions to WMS User / WMS Finance / WMS Manager.
# Those Role records have to exist before the doctypes are synced, otherwise the
# permission rows fail link validation during install.
before_install = "erpnext_wms.install.before_install"

scheduler_events = {
    "daily": [
        "erpnext_wms.tasks.generate_storage_charges",
    ]
}

# Submit/cancel behaviour lives on the Document subclasses themselves; hooking
# the same events again here would run the logic twice.
doc_events = {}
