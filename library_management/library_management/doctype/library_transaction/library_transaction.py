# Copyright (c) 2024, M Venkatesh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document # type: ignore
from frappe.model.docstatus import DocStatus # type: ignore


class LibraryTransaction(Document):
    def after_insert(self):
        if self.type == "Issue":
            self.validate_issue()
            self.validate_maximum_limit()
            self.validate_outstanding_fine()
            # set the article status to be Issued
            article = frappe.get_doc("Article", self.article)
            article.status = "Issued"
            article.custom_issued_member = self.library_member
            article.save()

        elif self.type == "Return":
            self.validate_return()
            # set the article status to be Available
            article = frappe.get_doc("Article", self.article)
            article.status = "Available"
            article.custom_issued_member = ""
            article.save()
            # calculate the outstanding amount and charge the ₹50  minus from the outstanding amount and update
            outstanding_fine = frappe.db.get_value(
                "Library Member",
                self.library_member,
                "custom_outstanding_amount",
            )
            outstanding_fine -= 50
            frappe.db.set_value(
                "Library Member",
                self.library_member,
                "custom_outstanding_amount",
                outstanding_fine,
            )


    def validate_issue(self):
        self.validate_member()
        article = frappe.get_doc("Article", self.article)
        # article cannot be issued if it is already issued
        if article.status == "Issued":
            frappe.throw("Article is already issued by another member")

    def validate_return(self):
        article = frappe.get_doc("Article", self.article)
        # article cannot be returned if it is not issued first
        if article.status == "Available":
            frappe.throw("Article cannot be returned without being issued first")

    def validate_maximum_limit(self):
        max_articles = frappe.db.get_single_value("Library Settings", "maximum_number_of_issued_articles")
        count = frappe.db.count(
            "Library Transaction",
            {"library_member": self.library_member, "type": "Issue", "docstatus": DocStatus.submitted()},
        )
        if count >= max_articles:
            frappe.throw("Maximum limit reached for issuing articles")

    def validate_membership(self):
        # check if a valid membership exist for this library member
        valid_membership = frappe.db.exists(
            "Library Membership",
            {
                "library_member": self.library_member,
                "docstatus": DocStatus.submitted(),
                "from_date": ("<", self.date),
                "to_date": (">", self.date),
            },
        )
        if not valid_membership:
            frappe.throw("The member does not have a valid membership")
    
    def validate_outstanding_fine(self):

        # check if the member has any outstanding fine
        outstanding_fine = frappe.db.get_value(
            "Library Member",
            self.library_member,
            "custom_outstanding_amount",
        )
        # check outstanding fine is lesser than 500 then thorw error that have less than 500 fine
        if outstanding_fine < 500:
            frappe.throw("You having outstanding amount less than 500")
        # check if the member has any outstanding fine

    def validate_member(self):
        # check if the member is valid
        if not frappe.db.exists("Library Member", self.library_member):
            frappe.throw("Invalid Library Member")
        # check if the member is valid
