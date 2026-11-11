import frappe
from pcpb_website.utils import service_by_slug, services

no_header = 1
show_sidebar = False
no_cache = 1


def get_context(context):
    slug = (frappe.form_dict.get("slug") or "").strip().lower()
    s = service_by_slug(slug)
    if not s:
        raise frappe.DoesNotExistError
    context.s = s
    by_name = {x.key: x for x in services()}
    context.related = [by_name[n] for n in s.related if n in by_name]
    context.title = s.name
    context.pcpb_own = 1
    context.pcpb_edit_link = f"/desk/pcpb-service-profile/{frappe.utils.quote(s.key)}"
