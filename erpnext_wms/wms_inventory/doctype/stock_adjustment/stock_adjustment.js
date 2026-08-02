// Live variance while counting. stock_adjustment.py recomputes all of this on
// validate() and remains authoritative -- and the actual Stock Reconciliation
// on submit is server-side only, it cannot be done from here.

frappe.ui.form.on("Stock Adjustment", {
	warehouse(frm) {
		// every row's current qty is warehouse-specific
		(frm.doc.adjustment_items || []).forEach((row) => fetch_current_qty(frm, row));
	},
});

frappe.ui.form.on("Adjustment Item", {
	item_code(frm, cdt, cdn) {
		fetch_current_qty(frm, locals[cdt][cdn]);
	},

	physical_qty(frm, cdt, cdn) {
		set_variance(frm, locals[cdt][cdn]);
	},

	rate(frm, cdt, cdn) {
		set_variance(frm, locals[cdt][cdn]);
	},

	adjustment_items_remove(frm) {
		set_total(frm);
	},
});

async function fetch_current_qty(frm, row) {
	if (!frm.doc.warehouse || !row.item_code) {
		return;
	}

	// core whitelisted method, so this works regardless of app controllers
	const { message } = await frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Bin",
			filters: { item_code: row.item_code, warehouse: frm.doc.warehouse },
			fieldname: "actual_qty",
		},
	});

	frappe.model.set_value(row.doctype, row.name, "current_qty", flt(message && message.actual_qty));
	set_variance(frm, row);
}

function set_variance(frm, row) {
	const variance = flt(row.physical_qty) - flt(row.current_qty);

	frappe.model.set_value(row.doctype, row.name, "variance", variance);
	frappe.model.set_value(row.doctype, row.name, "variance_value", variance * flt(row.rate));

	set_total(frm);
}

function set_total(frm) {
	frm.set_value(
		"total_variance_value",
		(frm.doc.adjustment_items || []).reduce((sum, row) => sum + flt(row.variance_value), 0)
	);
}
