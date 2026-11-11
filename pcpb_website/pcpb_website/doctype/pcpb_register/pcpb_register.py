import json
import re

import frappe
from frappe.model.document import Document


# addresses a register may not take, because the site or the portal already answers them
RESERVED = {"registers", "search", "page-builder", "website-guide", "online-services", "tenders", "news", "login", "signup", "portal",
            "apply", "verify", "services", "home", "me", "app", "desk", "api", "files", "assets", "private", "jobs", "contact", "about"}


class PCPBRegister(Document):
    def validate(self):
        self.slug = re.sub(r"[^a-z0-9-]+", "-", (self.slug or "").strip().lower()).strip("-")
        if not self.slug:
            frappe.throw("Address is required")
        self.route = re.sub(r"[^a-z0-9-]+", "-", (self.route or "").strip().strip("/").lower()).strip("-") or None
        if self.route:
            taken = RESERVED | set(frappe.get_all("Web Page", pluck="route")) | set(frappe.get_all("Web Form", pluck="route"))
            if self.route in taken:
                frappe.throw(f"The address /{self.route} is already used by a page, a form or the system. Choose another.")
        raw = (self.public_filter or "").strip()
        if raw:
            try:
                parsed = json.loads(raw)
            except Exception:
                frappe.throw("Which Records Are Public must be valid JSON, for example {\"status\": \"Registered\"}")
            if not isinstance(parsed, (dict, list)):
                frappe.throw("Which Records Are Public must be a JSON object, for example {\"status\": \"Registered\"}")
        if self.published and not raw:
            frappe.msgprint("This register shows nothing until 'Which Records Are Public' is filled in.", indicator="orange")

    def on_update(self):
        frappe.clear_cache(doctype="PCPB Register")
        frappe.cache.delete_value("pcpb_register_routes")
