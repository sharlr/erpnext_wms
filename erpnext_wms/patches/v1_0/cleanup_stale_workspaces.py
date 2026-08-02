import frappe

# Workspaces this app actually ships.
SHIPPED = ["File Management", "Warehouse Management", "Warehouse Visualization"]

WMS_MODULES = ["File Creation", "WMS Warehouse", "WMS Finance", "WMS Inventory"]


def execute():
	"""Drop Workspace records left behind by earlier versions of this app.

	`bench migrate` imports workspace JSON but never removes records whose file
	is gone. The old "File Creation" workspace is the damaging one: it slugs to
	/app/file-creation, and router.js resolves frappe.workspaces before
	doctype routes, so it permanently shadows the File Creation list view.
	"""
	if not frappe.db.table_exists("Workspace"):
		return

	stale = frappe.get_all(
		"Workspace",
		filters={"module": ("in", WMS_MODULES), "name": ("not in", SHIPPED)},
		pluck="name",
	)

	for name in stale:
		frappe.delete_doc(
			"Workspace",
			name,
			force=True,
			ignore_permissions=True,
			ignore_missing=True,
			delete_permanently=True,
		)
		print(f"erpnext_wms: removed stale workspace {name!r}")

	if stale:
		frappe.clear_cache()

	frappe.db.commit()
