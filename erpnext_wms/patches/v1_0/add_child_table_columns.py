from erpnext_wms.schema_repair import ensure_child_table_columns


def execute():
	"""Kept so existing Patch Log entries stay valid.

	The real work now runs from the after_migrate hook, which repeats on every
	migrate instead of once.
	"""
	ensure_child_table_columns()
