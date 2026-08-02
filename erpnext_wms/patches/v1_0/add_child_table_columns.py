import frappe

WMS_MODULES = ["File Creation", "WMS Warehouse", "WMS Finance", "WMS Inventory"]


def execute():
	"""Add parent/parenttype/parentfield to tables created as standard doctypes.

	frappe adds the child-table columns in DBTable.create() only, keyed off
	istable at the moment the table is first built (mariadb/schema.py:27).
	alter() iterates docfields and never revisits CHILD_TABLE_COLUMNS, so
	flipping istable 0 -> 1 on an existing doctype leaves the table without
	them -- and every child row insert dies with
	"Unknown column 'parent' in 'INSERT INTO'".
	"""
	child_doctypes = frappe.get_all(
		"DocType",
		filters={"istable": 1, "module": ("in", WMS_MODULES)},
		pluck="name",
	)

	for doctype in child_doctypes:
		if not frappe.db.table_exists(doctype):
			continue

		existing = {column.lower() for column in frappe.db.get_table_columns(doctype)}
		missing = [column for column in frappe.db.CHILD_TABLE_COLUMNS if column not in existing]

		if not missing:
			continue

		table = f"tab{doctype}"
		additions = ", ".join(
			f"ADD COLUMN `{column}` varchar({frappe.db.VARCHAR_LEN})" for column in missing
		)
		frappe.db.sql_ddl(f"ALTER TABLE `{table}` {additions}")

		if "parent" in missing:
			# child rows are always read via parent; create() indexes it too
			frappe.db.sql_ddl(f"ALTER TABLE `{table}` ADD INDEX IF NOT EXISTS `parent`(`parent`)")

		print(f"erpnext_wms: added {', '.join(missing)} to {table}")

	frappe.db.commit()
