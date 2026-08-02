import frappe

from erpnext_wms.schema_repair import WMS_MODULES


def check():
	"""Report the state of this app on the current site.

	Run with:
	    bench --site <site> execute erpnext_wms.diagnostics.check

	bench execute starts a fresh process, so this always reflects the code on
	disk -- unlike the web workers, which keep whatever they imported at boot.
	"""
	print("\n=== modules ===")
	for module in WMS_MODULES:
		app = frappe.db.get_value("Module Def", module, "app_name")
		print(f"  {module:<18} app_name={app or 'MISSING -- Module Def not found'}")

	print("\n=== doctypes ===")
	doctypes = frappe.get_all(
		"DocType",
		filters={"module": ("in", WMS_MODULES)},
		fields=["name", "custom", "istable", "autoname", "is_submittable"],
		order_by="istable, name",
	)

	if not doctypes:
		print("  NONE FOUND -- the app's doctypes are not on this site")

	for row in doctypes:
		controller = _controller_report(row.name)
		table = _table_report(row.name, row.istable)
		flags = []
		if row.custom:
			flags.append("CUSTOM=1 -> controller bypassed")
		if row.istable:
			flags.append("child")
		if row.is_submittable:
			flags.append("submittable")

		print(f"  {row.name:<22} autoname={row.autoname or '-':<16} {', '.join(flags) or '-'}")
		print(f"      controller: {controller}")
		print(f"      table:      {table}")

	print("\n=== workspaces ===")
	for row in frappe.get_all(
		"Workspace", filters={"module": ("in", WMS_MODULES)}, fields=["name", "module", "public"]
	):
		print(f"  {row.name:<28} module={row.module}")

	print("\n=== 3D visualisation ===")
	_visualisation_report()

	print("\n=== patch log ===")
	for row in frappe.get_all(
		"Patch Log", filters={"patch": ("like", "%erpnext_wms%")}, fields=["patch"]
	):
		print(f"  {row.patch}")

	print("")


def _visualisation_report():
	"""Every link in the chain that puts the 3D view on screen."""
	import os

	block = "WMS 3D Warehouse"
	if frappe.db.exists("Custom HTML Block", block):
		print(f"  Custom HTML Block '{block}': present")
	else:
		print(f"  Custom HTML Block '{block}': MISSING -- the workspace block renders nothing")

	# the iframe target; served from <app>/public via the sites/assets symlink
	source = frappe.get_app_path("erpnext_wms", "public", "warehouse-visualization.html")
	print(f"  source file: {'present' if os.path.exists(source) else 'MISSING'}  {source}")

	built = os.path.join(frappe.utils.get_bench_path(), "sites", "assets", "erpnext_wms")
	if os.path.exists(built):
		target = os.path.join(built, "warehouse-visualization.html")
		state = "present" if os.path.exists(target) else "MISSING -- run: bench build --app erpnext_wms"
		print(f"  served asset: {state}")
	else:
		print("  served asset: sites/assets/erpnext_wms MISSING -- run: bench build --app erpnext_wms")

	layouts = frappe.get_all("Warehouse Layout", fields=["name", "warehouse"])
	print(f"  Warehouse Layout records: {len(layouts)}")
	for row in layouts:
		locations = frappe.db.count("Warehouse Location", {"warehouse": row.warehouse})
		occupied = frappe.db.count(
			"Warehouse Location", {"warehouse": row.warehouse, "status": "Occupied"}
		)
		print(f"    {row.warehouse}: {locations} locations, {occupied} occupied")

	if not layouts:
		print("    none -- the warehouse dropdown will be empty")


def _controller_report(doctype):
	from frappe.model.base_document import get_controller

	try:
		cls = get_controller(doctype)
	except Exception as exc:  # noqa: BLE001 - this is a report, surface anything
		return f"FAILED TO RESOLVE -- {type(exc).__name__}: {exc}"

	if cls.__module__.startswith("frappe."):
		return f"{cls.__name__} from {cls.__module__} -- NOT the app controller"

	methods = [m for m in ("autoname", "before_naming", "validate", "on_submit") if hasattr(cls, m)]
	return f"{cls.__name__} from {cls.__module__} [{', '.join(methods) or 'no methods'}]"


def _table_report(doctype, istable):
	if not frappe.db.table_exists(doctype):
		return "MISSING"

	columns = {c.lower() for c in frappe.db.get_table_columns(doctype)}

	if not istable:
		return f"{len(columns)} columns"

	missing = [c for c in frappe.db.CHILD_TABLE_COLUMNS if c not in columns]
	if missing:
		return f"MISSING CHILD COLUMNS: {', '.join(missing)} -- child rows cannot insert"

	return f"{len(columns)} columns, child columns present"
