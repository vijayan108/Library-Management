# Copyright (c) 2024, M Venkatesh and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document # type: ignore


class LibraryMember(Document):
	def before_save(self):
		self.full_name = f"{self.first_name} {self.last_name}"
