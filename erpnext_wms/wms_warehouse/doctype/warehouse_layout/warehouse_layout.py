import frappe
from frappe import _
from frappe.model.document import Document


class WarehouseLayout(Document):
	pass


@frappe.whitelist()
def get_warehouse_occupancy(warehouse_name):
	"""Fetch warehouse occupancy data for 3D visualization."""
	if not warehouse_name:
		frappe.throw(_("Warehouse is required"))

	# get_doc raises DoesNotExistError on a missing filter match, so check
	# first rather than testing the return value for falsiness
	layout_name = frappe.db.get_value("Warehouse Layout", {"warehouse": warehouse_name}, "name")
	if not layout_name:
		frappe.throw(_("No layout found for warehouse: {0}").format(warehouse_name))

	layout = frappe.get_doc("Warehouse Layout", layout_name)
	layout.check_permission("read")

	locations = frappe.get_all(
		"Warehouse Location",
		filters={"warehouse": warehouse_name},
		fields=["name", "bin_x", "bin_y", "bin_z", "status", "file_creation"],
	)

	location_map = {}
	file_names = set()

	for loc in locations:
		key = f"{loc.bin_x}_{loc.bin_y}_{loc.bin_z}"
		location_map[key] = {
			"name": loc.name,
			"status": loc.status,
			"file_creation": loc.file_creation,
			"bin_x": loc.bin_x,
			"bin_y": loc.bin_y,
			"bin_z": loc.bin_z,
		}
		if loc.file_creation:
			file_names.add(loc.file_creation)

	# one query for every referenced file rather than get_doc per location
	file_details = {}
	if file_names:
		for row in frappe.get_all(
			"File Creation",
			filters={"name": ("in", list(file_names))},
			fields=["name", "file_type", "customer"],
		):
			file_details[row.name] = row

	return {
		"warehouse": warehouse_name,
		"layout_config": {
			"total_bins_x": layout.total_bins_x,
			"total_bins_y": layout.total_bins_y,
			"total_bins_z": layout.total_bins_z,
			"bin_width": layout.bin_width,
			"bin_height": layout.bin_height,
			"bin_depth": layout.bin_depth,
		},
		"occupancy": location_map,
		"file_details": file_details,
	}


@frappe.whitelist()
def get_warehouses():
	"""Get list of all warehouses with layouts."""
	return frappe.get_all("Warehouse Layout", fields=["warehouse"], distinct=True)
