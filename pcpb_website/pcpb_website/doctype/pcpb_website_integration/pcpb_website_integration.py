import frappe
from frappe.model.document import Document

SINGLE = "Single server (website and ERP together)"
WEBSITE = "Website server (ERP hosted separately)"
ERP = "ERP server (website hosted separately)"
INTEGRATION_ROLE = "PCPB Website Integration"


def _clean_url(v):
    v = (v or "").strip().rstrip("/")
    if v and not v.startswith(("http://", "https://")):
        v = "https://" + v
    return v


def _clean_path(v):
    v = (v or "").strip()
    return ("/" + v.lstrip("/")) if v and not v.startswith(("http://", "https://")) else v


class PCPBWebsiteIntegration(Document):
    def validate(self):
        self.erp_url = _clean_url(self.erp_url)
        if self.deployment_mode == WEBSITE and not (self.api_key and self.get_password("api_secret", raise_exception=False)):
            frappe.msgprint("Without an API Key and Secret the ERP treats this website like an ordinary visitor and limits its requests.",
                            indicator="orange", alert=True)
        seen = set()
        for p in self.portals:
            p.base_url = _clean_url(p.base_url)
            for f in ("sign_in_path", "sign_up_path", "home_path", "verify_path"):
                p.set(f, _clean_path(p.get(f)))
            if p.enabled and p.audience != "Other":
                if p.audience in seen:
                    frappe.throw(f"Only one enabled portal can have the audience {p.audience}.")
                seen.add(p.audience)

    def on_update(self):
        # answers fetched from the ERP are forgotten, so a changed address or key takes effect at once
        frappe.cache.delete_keys("pcpb_remote")
        frappe.clear_cache()


@frappe.whitelist()
def create_integration_user():
    """ERP server: make the user the website signs in as, with standard Frappe API keys. The secret is shown once."""
    frappe.only_for("System Manager")
    from frappe.core.doctype.user.user import generate_keys
    email = "website.integration@" + (frappe.local.site.split(":")[0] if "." in frappe.local.site else "pcpb.local")
    if not frappe.db.exists("User", email):
        user = frappe.get_doc({"doctype": "User", "email": email, "first_name": "Website", "last_name": "Integration",
                               "send_welcome_email": 0, "user_type": "System User"})
        user.append("roles", {"role": INTEGRATION_ROLE})
        user.insert(ignore_permissions=True)
    else:
        user = frappe.get_doc("User", email)
        if INTEGRATION_ROLE not in [r.role for r in user.roles]:
            user.append("roles", {"role": INTEGRATION_ROLE})
            user.save(ignore_permissions=True)
    secret = generate_keys(email)["api_secret"]
    frappe.db.set_single_value("PCPB Website Integration", "integration_user", email)
    frappe.db.commit()
    return {"user": email, "api_key": frappe.db.get_value("User", email, "api_key"), "api_secret": secret}
