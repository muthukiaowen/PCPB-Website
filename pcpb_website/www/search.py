import frappe

from pcpb_website.api import search_all
from pcpb_website.utils import lurl, tr, tr_value

no_cache = 1


def get_context(context):
    q = (frappe.form_dict.get("q") or "").strip()[:80]
    context.pcpb_own = 1
    context.q = q
    context.title = tr("search")
    context.hits = [frappe._dict(h, rows=[frappe._dict(r) for r in h["rows"]], columns=[frappe._dict(c) for c in h["columns"]])
                    for h in (search_all(q) if q else [])]
    pages = []
    if len(q) >= 2:
        like = f"%{q}%"
        for p in frappe.get_all("Web Page", filters={"published": 1, "title": ["like", like]}, fields=["title", "route"], limit=10):
            pages.append(frappe._dict(title=p.title, url=lurl("/" + (p.route or "")), kind=tr("page")))
        for p in frappe.get_all("PCPB Post", filters={"published": 1}, or_filters={"title": ["like", like], "summary": ["like", like]},
                                fields=["title", "route", "post_type"], limit=10, order_by="publish_date desc"):
            pages.append(frappe._dict(title=p.title, url=lurl("/" + (p.route or "")), kind=tr_value(p.post_type)))
        for t in frappe.get_all("PCPB Tender", filters={"published": 1}, or_filters={"title": ["like", like], "tender_no": ["like", like]},
                                fields=["name", "title"], limit=10):
            pages.append(frappe._dict(title=t.title, url=lurl(f"/tenders/{t.name}"), kind=tr("tenders_title")))
    context.pages = pages
