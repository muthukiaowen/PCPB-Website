import frappe

from pcpb_website.api import get_record

no_cache = 1


def get_context(context):
    slug = (frappe.form_dict.get("register") or "").strip().lower()
    name = frappe.form_dict.get("name")
    try:
        rec = get_record(slug, name)
    except Exception:
        raise frappe.DoesNotExistError
    context.pcpb_own = 1
    context.reg_slug = slug
    context.rec = frappe._dict(rec)
    context.title = str(rec["title"])
