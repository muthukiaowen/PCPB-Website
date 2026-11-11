import frappe
from frappe.model.document import Document

SINGLE_HOLDER = ("Board Chairperson", "Chief Executive Officer")


class PCPBLeader(Document):
    def validate(self):
        if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
            frappe.throw("Effective To cannot be before Effective From")
        if self.tenure_status == "Historical" and not self.effective_to:
            self.effective_to = frappe.utils.nowdate()
        if self.photo and not self.photo_alt:
            frappe.msgprint("Add a photo description (alt text) for accessibility.", indicator="orange", alert=True)

    def on_update(self):
        """When a new Chairperson or CEO is published, the previous holder becomes Historical. Nothing is deleted."""
        if self.leader_group in SINGLE_HOLDER and self.published and self.tenure_status == "Current":
            for name in frappe.get_all("PCPB Leader", filters={"leader_group": self.leader_group, "tenure_status": "Current",
                                                               "name": ["!=", self.name]}, pluck="name"):
                frappe.db.set_value("PCPB Leader", name, {"tenure_status": "Historical",
                                                          "effective_to": self.effective_from or frappe.utils.nowdate()})
