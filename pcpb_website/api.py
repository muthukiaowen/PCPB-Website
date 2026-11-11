"""Public register API.

A register is one PCPB Register record. It names the ERP record type it reads (Product, Premises, or any
other), the filter that decides which records are public, and the fields staff ticked as public.
Nothing else in those record types is reachable by guests. Nothing is copied: every request reads the ERP.

A field name may be "fieldname" or "table_field.child_fieldname" (e.g. "registrant.party_name"), which
shows that column of the child table, joined with commas.
"""
import csv
import io
import json

import frappe
from pcpb_website import remote
from pcpb_website.remote import public
from frappe.utils import formatdate, today

from pcpb_website.utils import lurl, tr_value


def _sub(o):
    """Filter tokens: "__today__" becomes today's date, so "valid until" rules stay live."""
    if isinstance(o, dict):
        return {k: _sub(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_sub(v) for v in o]
    return today() if o == "__today__" else o


def register_doc(slug, allow_unpublished=False):
    if not slug or not frappe.db.exists("PCPB Register", slug):
        frappe.throw("Unknown register", frappe.DoesNotExistError)
    r = frappe.get_cached_doc("PCPB Register", slug)
    if not r.published and not allow_unpublished:
        frappe.throw("Unknown register", frappe.DoesNotExistError)
    return r


def _cfg(slug):
    from pcpb_website.utils import can_edit
    r = register_doc(slug, allow_unpublished=can_edit())
    dt = r.source_doctype
    if not dt or not frappe.db.exists("DocType", dt):
        frappe.throw("This register has no data source yet", frappe.DoesNotExistError)
    raw = (r.public_filter or "").strip()
    try:
        base = _sub(json.loads(raw)) if raw else {}
    except Exception:
        base = {}
    if not base:
        # Fail closed: nothing is public until staff define what "public" means.
        frappe.throw("The public filter for this register has not been set", frappe.PermissionError)
    fields = [f for f in r.fields if f.public and _usable(dt, f.fieldname)]
    return r, dt, base, fields


def _usable(dt, fieldname):
    """A configured field that no longer exists on the record type is skipped, never an error for the public."""
    meta = frappe.get_meta(dt)
    if "." in fieldname:
        t, c = fieldname.split(".", 1)
        df = meta.get_field(t)
        return bool(df and df.fieldtype in ("Table", "Table MultiSelect") and frappe.get_meta(df.options).has_field(c))
    return meta.has_field(fieldname) or fieldname in ("name", "creation", "modified")


def _lab(f):
    return f.label or f.fieldname


def _with_filter(base, extra):
    if isinstance(base, dict):
        return {**base, **extra}
    return list(base) + [[k, "=", v] for k, v in extra.items()]


def _split(dt, fieldname):
    """-> (table_field, child_doctype, column) for dotted names, else (None, None, fieldname)."""
    if "." not in fieldname:
        return None, None, fieldname
    table, col = fieldname.split(".", 1)
    df = frappe.get_meta(dt).get_field(table)
    return table, df.options, col


def _child_filters(dt, table, child_dt, parents):
    """Child rows of a record. Where the child has a status that includes 'Superseded' (party and use
    rows), only the current ones are public; superseded history is never shown."""
    f = {"parenttype": dt, "parentfield": table}
    if parents is not None:
        f["parent"] = ["in", parents]
    sdf = frappe.get_meta(child_dt).get_field("status")
    if sdf and "Superseded" in (sdf.options or ""):
        f["status"] = "Active"
    return f


def _display(df, value):
    if value in (None, "") or df is None:
        return value
    if df.fieldtype == "Link":
        cache = frappe.local.__dict__.setdefault("pcpb_titles", {})
        key = (df.options, value)
        if key not in cache:
            tf = frappe.get_meta(df.options).title_field
            cache[key] = (frappe.db.get_value(df.options, value, tf) if tf and tf != "name" else None) or value
        return cache[key]
    if df.fieldtype == "Select":
        return tr_value(value)
    if df.fieldtype in ("Date", "Datetime"):
        return formatdate(value, "d MMM yyyy")
    if df.fieldtype == "Check":
        return "Yes" if value else "No"
    return value


def _fill(dt, names, fields, rows):
    """Direct columns come from the main query; dotted ones are gathered from child rows."""
    meta = frappe.get_meta(dt)
    today_s = today()
    for f in fields:
        table, child_dt, col = _split(dt, f.fieldname)
        if table:
            child = frappe.get_all(child_dt, filters=_child_filters(dt, table, child_dt, names),
                                   fields=["parent", col], order_by="idx asc") if names else []
            cdf = frappe.get_meta(child_dt).get_field(col)
            by = {}
            for c in child:
                v = _display(cdf, c.get(col))
                if v not in (None, ""):
                    by.setdefault(c.parent, []).append(str(v))
            for r in rows:
                r[f.fieldname] = ", ".join(by.get(r["name"], []))
        else:
            df = meta.get_field(col)
            for r in rows:
                raw = r.get(col)
                if df is not None and df.fieldtype == "Date" and raw and str(raw) < today_s:
                    r.setdefault("_expired", []).append(col)
                r[f.fieldname] = _display(df, raw)


def _direct(dt, fields):
    return [f.fieldname for f in fields if "." not in f.fieldname and f.fieldname != "name"]


def _search_filters(dt, fields, q):
    term = f"%{q.strip()[:80]}%"
    out = []
    for f in fields:
        if not f.searchable:
            continue
        table, child_dt, col = _split(dt, f.fieldname)
        if table:
            cf = _child_filters(dt, table, child_dt, None)
            cf[col] = ["like", term]
            hits = frappe.get_all(child_dt, filters=cf, pluck="parent", limit=500)
            if hits:
                out.append([dt, "name", "in", hits])
        else:
            out.append([dt, col, "like", term])
    return out


def _query(register, q=None, filters=None, start=0, page_length=None, sort=None, sort_dir=None, cap=100, all_fields=False):
    r, dt, base, fields = _cfg(register)
    meta = frappe.get_meta(dt)
    wide = lambda f: "." not in f.fieldname and meta.get_field(f.fieldname) is not None and meta.get_field(f.fieldname).fieldtype in (BODY_TYPES | FILE_TYPES)
    listable = [f for f in fields if not wide(f)]
    cols = listable if all_fields else ([f for f in listable if f.in_list] or listable[:4])
    user = json.loads(filters) if isinstance(filters, str) and filters else (filters or {})
    allowed = {f.fieldname for f in fields if f.filterable and "." not in f.fieldname}
    flt = _with_filter(base, {k: v for k, v in user.items() if k in allowed and v})
    empty = {"columns": [], "rows": [], "total": 0, "start": 0, "page_length": 25, "filterable": [], "title": r.title}
    or_filters = []
    if q and q.strip():
        or_filters = _search_filters(dt, fields, q)
        if not or_filters:
            return r, dt, cols, empty
    page_length = max(1, min(int(page_length or r.page_length or 25), cap))
    direct = set(_direct(dt, cols))
    sort = sort if sort in direct else (r.sort_field if r.sort_field in (direct | {"modified", "creation", "name"}) or
                                        (r.sort_field and frappe.get_meta(dt).has_field(r.sort_field)) else "modified")
    sort_dir = "desc" if (sort_dir or r.sort_dir or "asc").lower() == "desc" else "asc"
    kw = dict(filters=flt, or_filters=or_filters or None)
    total = frappe.get_all(dt, fields=[{"COUNT": "*", "as": "c"}], **kw)[0].c
    rows = frappe.get_all(dt, fields=["name", *sorted(direct)], start=int(start or 0), page_length=page_length,
                          order_by=f"{sort} {sort_dir}", **kw)
    _fill(dt, [x.name for x in rows], cols, rows)
    return r, dt, cols, {
        "title": r.title,
        "columns": [{"fieldname": c.fieldname, "label": _lab(c), "sortable": c.fieldname in direct} for c in cols],
        "filterable": [{"fieldname": f.fieldname, "label": _lab(f)} for f in fields if f.filterable and "." not in f.fieldname],
        "rows": rows, "total": total, "start": int(start or 0), "page_length": page_length,
        "sort": sort, "sort_dir": sort_dir, "kind": r.status_kind, "allow_export": int(r.allow_export or 0),
        "base_url": register_url(r),
    }


@frappe.whitelist(allow_guest=True)
@public(limit=180)
def list_register(register, q=None, filters=None, start=0, page_length=None, sort=None, sort_dir=None):
    if remote.on():
        out = remote.fetch("list_register", dict(register=register, q=q, filters=filters, start=start, page_length=page_length,
                                                 sort=sort, sort_dir=sort_dir))
        if out is None:
            frappe.throw("The register is not available right now", frappe.DoesNotExistError)
        return out
    return _query(register, q, filters, start, page_length, sort, sort_dir)[3]


@frappe.whitelist(allow_guest=True)
@public(limit=120)
def filter_options(register, fieldname):
    if remote.on():
        return remote.fetch("filter_options", dict(register=register, fieldname=fieldname), default=[])
    r, dt, base, fields = _cfg(register)
    if fieldname not in {f.fieldname for f in fields if f.filterable and "." not in f.fieldname}:
        frappe.throw("Not allowed", frappe.PermissionError)
    df = frappe.get_meta(dt).get_field(fieldname)
    vals = [v for v in frappe.get_all(dt, filters=_with_filter(base, {}), fields=[fieldname], group_by=fieldname,
                                      order_by=f"{fieldname} asc", pluck=fieldname, limit=300) if v]
    return [{"value": v, "label": _display(df, v)} for v in vals]


@frappe.whitelist(allow_guest=True)
@public(limit=120)
def get_record(register, name):
    if remote.on():
        out = remote.fetch("get_record", dict(register=register, name=name))
        if not out:
            frappe.throw("Record not found", frappe.DoesNotExistError)
        return out
    r, dt, base, fields = _cfg(register)
    detail = [f for f in fields if f.in_detail] or fields
    cols = set(_direct(dt, detail))
    if r.title_field and "." not in r.title_field and frappe.get_meta(dt).has_field(r.title_field):
        cols.add(r.title_field)
    rows = frappe.get_all(dt, filters=_with_filter(base, {"name": name}), fields=["name", *sorted(cols)], limit=1)
    if not rows:
        frappe.throw("Record not found", frappe.DoesNotExistError)
    title_raw = rows[0].get(r.title_field) if r.title_field else None
    _fill(dt, [name], detail, rows)
    title = title_raw or \
        next((rows[0].get(f.fieldname) for f in detail if rows[0].get(f.fieldname)), name)
    meta = frappe.get_meta(dt)
    values = []
    for f in detail:
        df = meta.get_field(f.fieldname) if "." not in f.fieldname else None
        kind = "body" if df is not None and df.fieldtype in BODY_TYPES else "file" if df is not None and df.fieldtype in FILE_TYPES else "text"
        value = rows[0].get(f.fieldname)
        if kind == "body" and value:
            value = frappe.utils.sanitize_html(value) if "<" in str(value) else frappe.utils.md_to_html(str(value))
        if kind == "file" and value and frappe.db.get_value("File", {"file_url": value}, "is_private"):
            value = ""  # a private attachment is never offered to the public
        values.append({"label": _lab(f), "fieldname": f.fieldname, "value": value, "type": kind})
    return {"name": name, "title": title, "register_title": r.title, "register_url": register_url(r), "kind": r.status_kind,
            "expired": rows[0].get("_expired") or [], "values": values}


@frappe.whitelist(allow_guest=True)
@public(limit=10)
def export_csv(register, q=None, filters=None):
    """Download what the public may see, as CSV. Capped so it cannot be used to strain the server."""
    if remote.on():
        from urllib.parse import urlencode
        query = urlencode({k: v for k, v in dict(register=register, q=q, filters=filters).items() if v})
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = f"{remote.erp_base()}/api/method/pcpb_website.api.export_csv?{query}"
        return
    r, dt, cols, out = _query(register, q, filters, 0, 5000, cap=5000, all_fields=False)
    if not int(r.allow_export or 0):
        frappe.throw("Download is not enabled for this register", frappe.PermissionError)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([c["label"] for c in out["columns"]])
    for row in out["rows"]:
        w.writerow([row.get(c["fieldname"]) or "" for c in out["columns"]])
    frappe.response["type"] = "binary"
    frappe.response["filename"] = f"{r.name}.csv"
    frappe.response["filecontent"] = ("﻿" + buf.getvalue()).encode("utf-8")
    frappe.response["content_type"] = "text/csv; charset=utf-8"


def register_url(r):
    """Public address of a register: its own address if it has one, else /registers/<slug>."""
    own = (r.get("route") or "").strip("/")
    return lurl("/" + own if own else f"/registers/{r.name}")


def registers(group=None):
    """Published registers with their group, for menus and index sections."""
    if remote.on():
        rows = [frappe._dict(r) for r in (remote.fetch("public_registers", default=[]) or [])]
        return [r for r in rows if not group or group == "All" or r.group == group]
    filters = {"published": 1}
    if group and group != "All":
        filters["register_group"] = group
    rows = frappe.get_all("PCPB Register", filters=filters,
                          fields=["name", "title", "route", "register_group", "description", "icon",
                                  "status_kind", "display_order"], order_by="display_order asc, title asc")
    groups = {g.name: g for g in frappe.get_all("PCPB Register Group", fields=["name", "description", "display_order"])}
    out = []
    for r in rows:
        g = groups.get(r.register_group)
        out.append(frappe._dict(
            slug=r.name, title=r.title, text=r.description or "",
            icon=r.icon or "leaf", kind=r.status_kind or "Standard", url=register_url(r), route=(r.route or "").strip("/"),
            group=r.register_group or "", group_title=r.register_group or "",
            group_text=(g.description or "") if g else "", group_order=(g.display_order if g else 999) or 0))
    out.sort(key=lambda x: (x.group_order, x.group))
    return out


def register_groups(group=None):
    out, seen = [], {}
    for r in registers(group):
        if r.group not in seen:
            seen[r.group] = frappe._dict(name=r.group, title=r.group_title, text=r.group_text, items=[])
            out.append(seen[r.group])
        seen[r.group]["items"].append(r)
    return out


def register_count(slug):
    if remote.on():
        return next((r.get("count") for r in registers() if r.slug == slug), None)
    try:
        r, dt, base, fields = _cfg(slug)
        return frappe.get_all(dt, filters=base, fields=[{"COUNT": "*", "as": "c"}])[0].c
    except Exception:
        return None


@frappe.whitelist(allow_guest=True)
@public(limit=60)
def search_all(q):
    """Search every published register at once (the product status check)."""
    q = (q or "").strip()[:80]
    if remote.on():
        return remote.fetch("search_all", dict(q=q), default=[]) if len(q) >= 2 else []
    out = []
    if len(q) < 2:
        return out
    for reg in registers():
        try:
            res = list_register(reg.slug, q=q, page_length=5)
        except Exception:
            continue
        if res.get("total"):
            out.append({"register": reg.slug, "title": reg.title, "kind": reg.kind, "total": res["total"], "url": reg.url,
                        "columns": res["columns"][:4], "rows": res["rows"]})
    order = {"Banned": 0, "Withdrawn": 1, "Restricted": 2}
    out.sort(key=lambda x: order.get(x["kind"], 5))
    return out


# ---- what a separately hosted website asks this (ERP) server for ---------------------------------
@frappe.whitelist(allow_guest=True)
@public(limit=60)
def public_registers():
    """Published registers with their record counts."""
    if remote.on():
        return remote.fetch("public_registers", default=[])
    out = []
    for r in registers():
        d = dict(r)
        d["count"] = register_count(r.slug)
        out.append(d)
    return out


@frappe.whitelist(allow_guest=True)
@public(limit=120)
def register_info(register):
    """Title, description and kind of one register, for the register page."""
    if remote.on():
        out = remote.fetch("register_info", dict(register=register))
        if not out:
            frappe.throw("Unknown register", frappe.DoesNotExistError)
        return out
    from pcpb_website.utils import can_edit
    r = register_doc((register or "").strip().lower(), allow_unpublished=can_edit())
    error = ""
    try:
        _cfg(r.name)
    except Exception as e:
        if not can_edit():
            frappe.throw("Unknown register", frappe.DoesNotExistError)
        error = str(e)
    return {"slug": r.name, "title": r.title, "description": r.description or "", "kind": r.status_kind, "url": register_url(r),
            "published": int(r.published or 0), "error": error}


@frappe.whitelist(allow_guest=True)
@public(limit=60)
def public_services():
    """The online services with their website descriptions, as the Services section shows them."""
    from pcpb_website.utils import services
    return [dict(s, action=dict(s.action)) for s in services()]


@frappe.whitelist(allow_guest=True)
@public(limit=60)
def public_vacancies(limit=50):
    from pcpb_website.utils import vacancies
    return [dict(v) for v in vacancies(limit)]


@frappe.whitelist(allow_guest=True)
@public(limit=30)
def link_status():
    """Answer to the website's Test connection button."""
    from pcpb_website.utils import services, site, vacancies
    return {"site_name": site().site_name, "deployment_mode": remote.mode(), "trusted": remote.trusted_caller(),
            "registers": len(registers()), "services": len(services()), "vacancies": len(vacancies())}


# ---- staff helper -------------------------------------------------------------------------------
SKIP = {"Section Break", "Column Break", "Tab Break", "Table", "Table MultiSelect", "HTML", "Button", "Password", "Image",
        "Geolocation", "Signature", "Code", "JSON", "Heading"}
# shown on the record page only: long text as an article body, attachments as download buttons
BODY_TYPES = {"Text Editor", "Text", "Long Text", "Markdown Editor", "HTML Editor"}
FILE_TYPES = {"Attach", "Attach Image"}
PUBLIC_CHILD_TYPES = {"Data", "Link", "Select", "Date", "Int", "Float"}


@frappe.whitelist()
def load_register_fields(register):
    """List every usable field of the register's record type (and table.column for its tables) as rows, all
    unticked, so staff only have to tick what the public may see."""
    frappe.only_for(["System Manager", "Website Manager"])
    r = frappe.get_doc("PCPB Register", register)
    dt = r.source_doctype
    have = {f.fieldname for f in r.fields}
    added = 0
    for df in frappe.get_meta(dt).fields:
        cands = []
        if df.fieldtype in ("Table", "Table MultiSelect"):
            for c in frappe.get_meta(df.options).fields:
                if c.fieldtype in PUBLIC_CHILD_TYPES and not c.hidden:
                    cands.append((f"{df.fieldname}.{c.fieldname}", f"{df.label}: {c.label or c.fieldname}"))
        elif df.fieldtype not in SKIP and not df.hidden:
            cands.append((df.fieldname, df.label or df.fieldname))
        for fn, lab in cands:
            if fn not in have:
                r.append("fields", {"fieldname": fn, "label": lab, "public": 0, "in_list": 0, "in_detail": 0})
                added += 1
    r.save()
    return added


@frappe.whitelist()
def add_publish_tick(register):
    """Give the register's record type a 'Publish on Website' tick (a standard Custom Field) and make it the public
    filter. Staff then publish a record to the website by ticking it on the ERP record, like any publish switch."""
    frappe.only_for(["System Manager", "Website Manager"])
    from frappe.custom.doctype.custom_field.custom_field import create_custom_field
    r = frappe.get_doc("PCPB Register", register)
    dt = r.source_doctype
    meta = frappe.get_meta(dt)
    if not meta.has_field("publish_on_website"):
        create_custom_field(dt, {"fieldname": "publish_on_website", "fieldtype": "Check", "label": "Publish on Website",
                                 "insert_after": meta.fields[-1].fieldname if meta.fields else None, "allow_on_submit": 1,
                                 "description": f"Shows this record on the website in: {r.title}"})
        frappe.clear_cache(doctype=dt)
    r.public_filter = json.dumps({"publish_on_website": 1})
    r.save()
    return "ok"


@frappe.whitelist(allow_guest=True, methods=["GET"])
def app_logo():
    """The picture of the PCPB Website icon on the Desk home screen. The icon points here, and this forwards to the
    logo uploaded for the website, so the icon changes the moment a new logo is uploaded. Nothing private is exposed:
    a logo kept as a private file is not used."""
    from pcpb_website.pcpb_website.doctype.pcpb_website_settings.pcpb_website_settings import desk_icon_url
    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = desk_icon_url()
