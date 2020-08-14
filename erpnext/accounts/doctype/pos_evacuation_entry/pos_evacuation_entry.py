# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
from frappe.model.document import Document
from erpnext.controllers.status_updater import StatusUpdater

class POSEvacuationEntry(StatusUpdater):
	def validate(self):
		self.validate_pos_profile_and_cashier()
		self.set_status()
	
	def onload(self):
		frappe.msgprint(str(get_total_evacuation(self.pos_opening_entry, self.mode_of_payment)))


	def validate_pos_profile_and_cashier(self):
		if self.company != frappe.db.get_value("POS Profile", self.pos_profile, "company"):
			frappe.throw(_("POS Profile {} does not belongs to company {}".format(self.pos_profile, self.company)))

		if not cint(frappe.db.get_value("User", self.user, "enabled")):
			frappe.throw(_("User {} has been disabled. Please select valid user/cashier".format(self.user)))

	def on_submit(self):
		self.set_status(update=True)


@frappe.whitelist()
def get_total_evacuation(opening_entry_name, mode_of_payment):
	query = """ SELECT SUM(cash_amount) as sum_amount 
			FROM `tabPOS Evacuation Entry` 
			WHERE 
				pos_opening_entry = '%s'
				AND mode_of_payment = '%s'
				AND status = 'Open'
				AND docstatus= 1 
			
			""" %(opening_entry_name,mode_of_payment)

	return frappe.db.sql(query,as_dict=True)[0]["sum_amount"] or 0