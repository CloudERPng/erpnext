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

	def validate_pos_profile_and_cashier(self):
		if self.company != frappe.db.get_value("POS Profile", self.pos_profile, "company"):
			frappe.throw(_("POS Profile {} does not belongs to company {}".format(self.pos_profile, self.company)))

		if not cint(frappe.db.get_value("User", self.user, "enabled")):
			frappe.throw(_("User {} has been disabled. Please select valid user/cashier".format(self.user)))

	def on_submit(self):
		self.set_status(update=True)
		self.journal_entry = self.make_journal_entry()


	def make_journal_entry(self):
		pos_profile = frappe.get_doc("POS Profile", self.pos_profile)
		default_currency = frappe.get_value("Company", self.company, "default_currency")
		cash_account = get_bank_cash_account(self.mode_of_payment, self.company)
		jl_rows = []
		debit_row = dict(
			account = pos_profile.evacuation_cash_account,
			debit_in_account_currency = self.cash_amount,
			account_curremcy = default_currency,
			cost_center =  pos_profile.cost_center or "",
		)
		jl_rows.append(debit_row)

		credit_row = dict(
			account = cash_account,
			credit_in_account_currency = self.cash_amount,
			account_curremcy = default_currency,
			cost_center =  pos_profile.cost_center or "",
		)
		jl_rows.append(credit_row)

		user_remark = "Against " + self.doctype + " : " + self.name
		jv_doc = frappe.get_doc(dict(
			doctype = "Journal Entry",
			posting_date = self.posting_date,
			accounts = jl_rows,
			company = self.company,
			multi_currency = 0,
			user_remark = user_remark
		))

		jv_doc.flags.ignore_permissions = True
		frappe.flags.ignore_account_permission = True
		jv_doc.save()
		jv_doc.submit()
		return jv_doc.name


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


def get_bank_cash_account(mode_of_payment, company):
	account = frappe.db.get_value("Mode of Payment Account",
		{"parent": mode_of_payment, "company": company}, "default_account")
	if not account:
		frappe.throw(_("Please set default Cash or Bank account in Mode of Payment {0}")
			.format(mode_of_payment))
	return account