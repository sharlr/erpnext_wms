// Populates the payment voucher table and keeps the totals live as the form is
// edited. The controller does the same on validate() and stays authoritative on
// save; this exists so the figures appear while the user is still typing.
//
// Customer, Company and File Type are not touched here -- they come from
// fetch_from on the doctype and populate the moment File Number is picked.

frappe.ui.form.on("WMS Invoice", {
	file_creation(frm) {
		load_payment_vouchers(frm);
	},

	paid_amount(frm) {
		calculate_totals(frm);
	},
});

frappe.ui.form.on("Invoice Item", {
	quantity(frm, cdt, cdn) {
		set_row_amount(frm, cdt, cdn);
	},

	rate(frm, cdt, cdn) {
		set_row_amount(frm, cdt, cdn);
	},

	invoice_items_remove(frm) {
		calculate_totals(frm);
	},
});

function set_row_amount(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", flt(row.quantity) * flt(row.rate));
	calculate_totals(frm);
}

async function load_payment_vouchers(frm) {
	frm.clear_table("aggregated_payments");

	if (!frm.doc.file_creation) {
		frm.refresh_field("aggregated_payments");
		calculate_totals(frm);
		return;
	}

	// core whitelisted method, so this works regardless of app controllers
	const { message: vouchers } = await frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Payment Voucher",
			filters: { file_creation: frm.doc.file_creation, docstatus: 1 },
			fields: ["name", "payment_date", "amount"],
			order_by: "payment_date asc",
			limit_page_length: 0,
		},
	});

	for (const voucher of vouchers || []) {
		const row = frm.add_child("aggregated_payments");
		row.payment_voucher = voucher.name;
		row.payment_date = voucher.payment_date;
		row.payment_amount = voucher.amount;
	}

	frm.refresh_field("aggregated_payments");
	calculate_totals(frm);
}

function calculate_totals(frm) {
	const payments = (frm.doc.aggregated_payments || []).reduce(
		(sum, row) => sum + flt(row.payment_amount),
		0
	);
	const services = (frm.doc.invoice_items || []).reduce((sum, row) => sum + flt(row.amount), 0);

	frm.set_value("total_amount", payments + services);
	frm.set_value("balance", payments + services - flt(frm.doc.paid_amount));
}
