import frappe


def generate_storage_charges():
	"""Daily scheduler entry point.

	Referenced by `scheduler_events` in hooks.py. Storage-charge rating is not
	implemented yet, so this deliberately does nothing rather than raising --
	a scheduler job that throws is retried and fills the error log every day.
	"""
	frappe.logger("erpnext_wms").debug("generate_storage_charges: no-op, rating rules not configured")
