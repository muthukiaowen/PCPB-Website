"""The visual page builder. /page-builder lists the pages; /page-builder?page=<name> edits one."""
import os

import frappe

from pcpb_website.render import page_context
from pcpb_website.utils import can_edit

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/page-builder"
        raise frappe.Redirect
    if not can_edit():
        frappe.throw("You are not allowed to edit the website", frappe.PermissionError)
    context.pcpb_own = 1
    context.pcpb_edit = 1
    context.title = "Website builder"
    context.pb_version = str(int(os.path.getmtime(frappe.get_app_path("pcpb_website", "public", "js", "builder.js"))))
    page = frappe.form_dict.get("page")
    context.pb_page = ""
    if page and frappe.db.exists("Web Page", page):
        doc = frappe.get_doc("Web Page", page)
        page_context(doc, context, edit=True, use_draft=True)
        context.pb_page = doc.name
        context.title = f"Editing: {doc.title}"
