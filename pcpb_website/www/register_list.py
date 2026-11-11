import frappe

from pcpb_website.api import register_info

no_cache = 1


def get_context(context):
    slug = (frappe.form_dict.get("register") or "").strip().lower()
    try:
        r = frappe._dict(register_info(slug))
    except Exception:
        raise frappe.DoesNotExistError
    context.pcpb_own = 1
    context.reg_slug, context.reg_kind, context.reg_published = r.slug, r.kind, int(r.published or 0)
    context.title = r.title
    context.reg_text = r.description or ""
    context.reg_error = r.get("error") or ""
    context.pcpb_edit_link = f"/desk/pcpb-register/{r.slug}"
