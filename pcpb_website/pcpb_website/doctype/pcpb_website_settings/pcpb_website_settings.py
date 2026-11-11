import frappe
from frappe.model.document import Document


class PCPBWebsiteSettings(Document):
    def on_update(self):
        sync_desk_logo(self)
        frappe.clear_cache()


def sync_desk_logo(settings=None):
    """One logo for the organisation: the logo uploaded for the website is also the logo of the Desk and the sign-in
    page. Runs when the settings are saved and after every migrate. A Desk logo chosen by hand in Navbar Settings is
    never replaced: only an empty one, or one this function put there earlier. The PCPB Website icon on the Desk
    home screen follows the logo by itself (see api.app_logo)."""
    s = settings or frappe.get_cached_doc("PCPB Website Settings")
    logo = (s.get("logo") or "").strip()
    usable = bool(logo) and not logo.startswith("/private/") and bool(s.get("logo_on_desk"))
    last = s.get("desk_logo_set") or ""

    for dt in ("Navbar Settings", "Website Settings"):
        if not frappe.get_meta(dt).has_field("app_logo"):
            continue
        current = frappe.db.get_single_value(dt, "app_logo") or ""
        if usable and current != logo and (not current or current == last):
            frappe.db.set_single_value(dt, "app_logo", logo)
        elif not usable and current and current == last:
            frappe.db.set_single_value(dt, "app_logo", "")

    new = logo if usable else ""
    if new != last:
        frappe.db.set_single_value("PCPB Website Settings", "desk_logo_set", new)


DEFAULT_ICON = "/assets/pcpb_website/images/pcpb-logo.svg"


def desk_icon_url():
    s = frappe.get_cached_doc("PCPB Website Settings")
    logo = (s.get("logo") or "").strip()
    if logo and s.get("logo_on_desk") and not logo.startswith("/private/"):
        return logo
    return DEFAULT_ICON
