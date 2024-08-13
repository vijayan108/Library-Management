# Copyright (c) 2024, M Venkatesh and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document # type: ignore
from frappe.model.docstatus import DocStatus # type: ignore


class LibraryMembership(Document):
	def before_save(self):
		existing_membership = frappe.db.exists("Library Membership", {
			"library_member": self.library_member,
			"docstatus": DocStatus.submitted(),
			"to_date": (">", self.from_date),
		},
		)
		if existing_membership:
			frappe.throw(
				f"Another active membership exists for {self.library_member}"
			)

		# get loan period and compute to_date by adding loan_period to from_date
		loan_period = frappe.db.get_single_value("Library Settings", "loan_period")
		self.to_date = frappe.utils.add_days(self.from_date, loan_period or 30)