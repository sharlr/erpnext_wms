// Keeps the naming series in step with File Type so an Import file is named
// IM-YYYY-##### and an Export file EX-YYYY-#####.
//
// This lives in the form script rather than the Python controller on purpose:
// doctype JS is read from disk into the doctype meta, so it takes effect on
// `bench migrate` / `bench clear-cache` without restarting the bench.

const SERIES_BY_TYPE = {
	Import: "IM-.YYYY.-",
	Export: "EX-.YYYY.-",
};

frappe.ui.form.on("File Creation", {
	file_type(frm) {
		apply_series(frm);
	},

	refresh(frm) {
		// covers a file_type arriving as a route option or a default
		apply_series(frm);
	},
});

function apply_series(frm) {
	// the series is baked into the name at insert, so never touch a saved doc
	if (!frm.is_new()) {
		return;
	}

	const series = SERIES_BY_TYPE[frm.doc.file_type];
	if (series && frm.doc.naming_series !== series) {
		frm.set_value("naming_series", series);
	}
}
