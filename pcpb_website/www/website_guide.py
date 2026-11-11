"""Staff help. The guide is kept as standard Help Articles (category PCPB Website Administration), so a
Website Manager edits it in the Desk. This page shows them to signed-in website staff only."""
import frappe

from pcpb_website.builder import README_URL
from pcpb_website.install import HELP_CATEGORY
from pcpb_website.utils import can_edit, is_manager

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/website-guide"
        raise frappe.Redirect
    if not can_edit():
        frappe.throw("This guide is for website staff", frappe.PermissionError)
    rows = frappe.get_all("Help Article", filters={"category": HELP_CATEGORY}, fields=["name", "title", "content", "level"],
                          order_by="creation asc") if frappe.db.exists("DocType", "Help Article") else []
    context.pcpb_own = 1
    context.title = "Website guide"
    context.articles = [frappe._dict(r, anchor=frappe.scrub(r.title).replace("_", "-"), edit=f"/desk/help-article/{frappe.utils.quote(r.name)}") for r in rows]
    context.can_manage = is_manager()
    context.new_url = "/desk/help-article/new"
    context.readme_url = README_URL
