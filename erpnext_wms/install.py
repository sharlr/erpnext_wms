import frappe

def after_install():
    """Create roles after app installation"""
    frappe.db.set_value("Module", "WMS Warehouse", "module_name", "erpnext_wms")
    
    roles = [
        {"name": "WMS User", "description": "Warehouse Management System User"},
        {"name": "WMS Finance", "description": "WMS Finance Manager"},
        {"name": "WMS Manager", "description": "WMS System Administrator"}
    ]
    
    for role in roles:
        if not frappe.db.exists("Role", role["name"]):
            frappe.get_doc({
                "doctype": "Role",
                "name": role["name"],
                "role_name": role["name"],
                "desk_access": 1
            }).insert(ignore_permissions=True)
    
    frappe.msgprint("ERPNext WMS installed successfully!")
