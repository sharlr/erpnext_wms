import frappe

WMS_MODULES = ["File Creation", "WMS Warehouse", "WMS Finance", "WMS Inventory"]


def repair():
	"""after_migrate entry point: everything that has to be reasserted."""
	ensure_standard_doctypes()
	ensure_child_table_columns()


def ensure_standard_doctypes():
	"""Force custom=0 on this app's doctypes.

	import_controller() returns the plain Document class -- silently, with no
	traceback -- for any doctype flagged custom (base_document.py:105). That is
	the only path in frappe where a controller is skipped without raising, and
	it disables autoname(), validate(), on_submit() and every other method at
	once. A doctype that was ever created through the UI keeps the flag.
	"""
	flagged = frappe.get_all(
		"DocType",
		filters={"custom": 1, "module": ("in", WMS_MODULES)},
		pluck="name",
	)

	for doctype in flagged:
		frappe.db.set_value("DocType", doctype, "custom", 0, update_modified=False)
		print(f"erpnext_wms: cleared custom flag on {doctype} (controller was being bypassed)")

	if flagged:
		frappe.clear_cache()
		frappe.db.commit()

	return flagged


def ensure_child_table_columns():
	"""Add parent/parenttype/parentfield to child tables that lack them.

	frappe writes the child-table columns in DBTable.create() only, keyed off
	istable at the moment the table is first built (mariadb/schema.py:27).
	alter() builds its column list from docfields and never revisits
	CHILD_TABLE_COLUMNS, so a doctype whose table predates istable=1 keeps a
	standard-table shape forever and every child row insert fails with
	"Unknown column 'parent' in 'INSERT INTO'".

	Wired to after_migrate rather than left as a one-shot patch: patches are
	recorded in Patch Log and never retried, so a patch that ran early -- or
	ran before the doctype existed -- would leave the table broken with no way
	to re-trigger it short of editing the log.

	Safe to run repeatedly; it only touches tables that are missing columns.
	"""
	repaired = []

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
			# child rows are always looked up by parent; create() indexes it too
			frappe.db.sql_ddl(f"ALTER TABLE `{table}` ADD INDEX IF NOT EXISTS `parent`(`parent`)")

		repaired.append(f"{table}: added {', '.join(missing)}")

	frappe.db.commit()

	if repaired:
		for line in repaired:
			print(f"erpnext_wms: {line}")
	else:
		print(f"erpnext_wms: child tables OK ({len(child_doctypes)} checked)")

	return repaired
