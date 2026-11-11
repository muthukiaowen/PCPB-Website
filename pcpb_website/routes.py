"""A register can have an address of its own, for example /memos instead of /registers/memos.

This renderer answers /<address> and /<address>/<record> for registers that set one. It is asked first for every
website request, so the check is a lookup in a small cached table and nothing else."""
import frappe
from frappe.website.page_renderers.base_renderer import BaseRenderer
from frappe.website.page_renderers.template_page import TemplatePage

CACHE_KEY = "pcpb_register_routes"


def route_map():
    """own address -> register slug, for published registers that have one."""
    cached = frappe.cache.get_value(CACHE_KEY)
    if cached is not None:
        return cached
    try:
        from pcpb_website import api
        out = {r.route: r.slug for r in api.registers() if r.get("route")}
    except Exception:
        out = {}
    frappe.cache.set_value(CACHE_KEY, out, expires_in_sec=300)
    return out


class RegisterPage(BaseRenderer):
    def can_render(self):
        parts = [p for p in self.path.split("/") if p]
        if not 1 <= len(parts) <= 2:
            return False
        slug = route_map().get(parts[0].lower())
        if not slug:
            return False
        self.slug, self.record = slug, parts[1] if len(parts) == 2 else None
        return True

    def render(self):
        frappe.form_dict.register = self.slug
        if self.record:
            frappe.form_dict.name = self.record
        return TemplatePage("register-record" if self.record else "register-list", self.http_status_code).render()
