// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('POS Evacuation Entry', {
	// refresh: function(frm) {

	// }
	onload: function(frm) {
		frm.set_query("pos_opening_entry", function(doc) {
			return { filters: { 'status': 'Open', 'docstatus': 1 } };
		});
		
	},
});
