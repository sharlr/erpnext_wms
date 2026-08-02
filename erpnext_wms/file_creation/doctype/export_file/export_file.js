// Live totals as items are entered. export_file.py recomputes the same figures
// on validate() and stays authoritative on save.
//
// Customer, Company, Shipping Line, Destination Country and AWB/BL come from
// fetch_from on the doctype, so they populate as soon as File Number is picked.

frappe.ui.form.on("Export Item", {
	quantity(frm, cdt, cdn) {
		set_row_amount(frm, cdt, cdn);
	},

	rate(frm, cdt, cdn) {
		set_row_amount(frm, cdt, cdn);
	},

	weight(frm) {
		calculate_totals(frm);
	},

	export_items_remove(frm) {
		calculate_totals(frm);
	},
});

function set_row_amount(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", flt(row.quantity) * flt(row.rate));
	calculate_totals(frm);
}

function calculate_totals(frm) {
	const rows = frm.doc.export_items || [];

	frm.set_value(
		"total_quantity",
		rows.reduce((sum, row) => sum + flt(row.quantity), 0)
	);
	frm.set_value(
		"total_weight",
		rows.reduce((sum, row) => sum + flt(row.weight) * flt(row.quantity), 0)
	);
	frm.set_value(
		"total_value",
		rows.reduce((sum, row) => sum + flt(row.amount), 0)
	);
}
