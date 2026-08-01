import frappe
from frappe.model.document import Document


class WarehouseLayout(Document):
	pass


@frappe.whitelist()
def get_warehouse_occupancy(warehouse_name):
	"""Fetch warehouse occupancy data for 3D visualization"""
	layout = frappe.get_doc("Warehouse Layout", {"warehouse": warehouse_name})

	if not layout:
		frappe.throw(f"No layout found for warehouse: {warehouse_name}")

	# Fetch all warehouse locations for this warehouse
	locations = frappe.get_all(
		"Warehouse Location",
		filters={"warehouse": warehouse_name},
		fields=["name", "bin_x", "bin_y", "bin_z", "status", "file_creation"]
	)

	# Build occupancy grid
	occupancy_grid = []
	location_map = {}

	for loc in locations:
		key = f"{loc.bin_x}_{loc.bin_y}_{loc.bin_z}"
		location_map[key] = {
			"name": loc.name,
			"status": loc.status,
			"file_creation": loc.file_creation,
			"bin_x": loc.bin_x,
			"bin_y": loc.bin_y,
			"bin_z": loc.bin_z
		}

	# Get File Creation details for labels
	file_details = {}
	for loc in locations:
		if loc.file_creation and loc.file_creation not in file_details:
			file_doc = frappe.get_doc("File Creation", loc.file_creation)
			file_details[loc.file_creation] = {
				"name": file_doc.name,
				"file_type": file_doc.file_type,
				"customer": file_doc.customer
			}

	return {
		"warehouse": warehouse_name,
		"layout_config": {
			"total_bins_x": layout.total_bins_x,
			"total_bins_y": layout.total_bins_y,
			"total_bins_z": layout.total_bins_z,
			"bin_width": layout.bin_width,
			"bin_height": layout.bin_height,
			"bin_depth": layout.bin_depth
		},
		"occupancy": location_map,
		"file_details": file_details
	}


@frappe.whitelist()
def get_warehouses():
	"""Get list of all warehouses with layouts"""
	warehouses = frappe.get_all(
		"Warehouse Layout",
		fields=["warehouse"],
		distinct=True
	)
	return warehouses
