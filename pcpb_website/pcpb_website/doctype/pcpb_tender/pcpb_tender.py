import frappe
from frappe.model.document import Document


class PCPBTender(Document):
    def validate(self):
        if self.closing_on and self.published_on and frappe.utils.getdate(self.closing_on) < frappe.utils.getdate(self.published_on):
            frappe.throw("Closing date cannot be before the published date")
        if self.tender_status == "Awarded" and not self.award_note:
            frappe.msgprint("Add an award notice (bidder and date) before publishing the award.", indicator="orange", alert=True)

    @property
    def effective_status(self):
        """Open tenders whose closing time has passed read as Closed without anyone editing them."""
        if self.tender_status == "Open" and self.closing_on and frappe.utils.get_datetime(self.closing_on) < frappe.utils.now_datetime():
            return "Closed"
        return self.tender_status
