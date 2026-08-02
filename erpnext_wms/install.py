import frappe

ROLES = [
	{"name": "WMS User", "desk_access": 1},
	{"name": "WMS Finance", "desk_access": 1},
	{"name": "WMS Manager", "desk_access": 1},
]


def before_install():
	"""Create the roles the doctype permissions link to.

	This has to run before the doctypes are synced -- a permission row pointing
	at a Role that does not exist yet fails link validation.
	"""
	for role in ROLES:
		if frappe.db.exists("Role", role["name"]):
			continue

		frappe.get_doc(
			{
				"doctype": "Role",
				"role_name": role["name"],
				"desk_access": role["desk_access"],
			}
		).insert(ignore_permissions=True)

	frappe.db.commit()
