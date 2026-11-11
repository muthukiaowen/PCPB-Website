"""Server side of the visual page builder (/page-builder).

Editors drag sections, type text and drop pictures on the page itself. What they save is a draft kept on the
standard Web Page. The draft becomes the live page when the page reaches a published state of the Web Page
workflow (Desk > Workflow), so who may publish is decided there, not in code.
"""
import json
import re

import frappe
from frappe.utils import cint
from frappe import _

from pcpb_website.render import apply_draft, draft_of, live_blocks, render_block
from pcpb_website.utils import EDIT_ROLES, can_edit, is_manager, site, theme_vars

THEME_FIELDS = ["color_primary", "color_dark", "color_accent", "color_soft", "color_bg", "color_text", "font_body",
                "font_heading", "radius", "page_width", "show_flag_bar", "allow_dark_mode", "allow_text_size"]


def _guard(manager=False):
    if not can_edit() or (manager and not is_manager()):
        frappe.throw(_("You are not allowed to edit the website"), frappe.PermissionError)


def _catalogue():
    path = frappe.get_app_path("pcpb_website", "sections.json")
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def _field(df):
    return {"fieldname": df.fieldname, "label": df.label, "fieldtype": df.fieldtype, "options": df.options or "",
            "default": df.default, "reqd": int(df.reqd or 0)}


def _library():
    cat = _catalogue()
    out = []
    for name in frappe.get_all("Web Template", filters={"type": "Section"}, pluck="name", order_by="name asc"):
        t = frappe.get_cached_doc("Web Template", name)
        meta = cat.get(name) or {}
        if meta.get("hidden"):
            continue
        out.append({"name": name, "label": meta.get("label") or name, "category": meta.get("category") or ("Other" if name.startswith("PCPB ") else "Frappe standard"),
                    "description": meta.get("description") or "", "icon": meta.get("icon") or "square", "order": meta.get("order", 500),
                    "data": meta.get("data") or "", "fields": [_field(f) for f in t.fields]})
    out.sort(key=lambda x: (x["order"], x["label"]))
    return out


def _workflow(doc):
    """State of the page in the Web Page workflow, and what this user may do next. Nothing about the steps is
    assumed here: they are read from the Workflow record."""
    from frappe.model.workflow import get_transitions, get_workflow_name
    name = get_workflow_name("Web Page")
    if not name:
        return None
    try:
        transitions = get_transitions(doc)
    except Exception:
        transitions = []
    wf = frappe.get_cached_doc("Workflow", name)
    first = wf.states[0].state if wf.states else ""
    state = doc.get("workflow_state") or first
    live_states = list(dict.fromkeys(s.state for s in wf.states if s.update_field == "published" and str(s.update_value) == "1"))
    actions = list(dict.fromkeys(t.get("action") for t in transitions))
    # the step that sends a fresh draft onwards for approval: from the first state to a state that is neither live nor the first
    send = next((t.get("action") for t in transitions if state == first and t.get("next_state") not in live_states + [first]), None)
    # steps that only take a live page back to the first state: saving a draft already does that, so no button is needed
    back = [t.get("action") for t in transitions if state in live_states and t.get("next_state") == first]
    return {"name": name, "state": state, "actions": actions, "live_states": live_states, "send_action": send, "back_actions": back}


def _page_state(doc):
    draft = draft_of(doc)
    return {
        "name": doc.name, "route": doc.route, "published": int(doc.published or 0), "has_draft": bool(draft),
        "title": (draft or {}).get("title") or doc.title,
        "meta_description": (draft.get("meta_description") if draft else doc.meta_description) or "",
        "blocks": draft["blocks"] if draft else live_blocks(doc),
        "is_builder": doc.content_type == "Page Builder" or bool(draft),
        "workflow": _workflow(doc), "is_home": (frappe.db.get_single_value("Website Settings", "home_page") or "") == doc.route,
    }


@frappe.whitelist()
def state(page=None):
    _guard()
    s = site()
    out = {
        "library": _library(), "is_manager": is_manager(),
        "pages": pages(),
        "theme": {f: s.get(f) for f in THEME_FIELDS},
        "theme_options": {"font_body": ["Inter", "System", "Arial", "Georgia", "Verdana"], "font_heading": ["Serif", "Same as body", "Georgia"]},
    }
    if page:
        out["page"] = _page_state(frappe.get_doc("Web Page", page))
    return out


@frappe.whitelist()
def pages():
    _guard()
    rows = frappe.get_all("Web Page", fields=["name", "title", "route", "published", "content_type", "modified", "pcpb_draft"],
                          order_by="title asc", limit=500)
    has_wf = frappe.get_meta("Web Page").has_field("workflow_state")
    states = dict(frappe.get_all("Web Page", fields=["name", "workflow_state"], as_list=True, limit=500)) if has_wf else {}
    home = frappe.db.get_single_value("Website Settings", "home_page") or ""
    return [{"name": r.name, "title": r.title, "route": r.route, "published": int(r.published or 0),
             "builder": r.content_type == "Page Builder", "has_draft": bool(r.pcpb_draft), "state": states.get(r.name) or "",
             "is_home": r.route == home, "modified": str(r.modified)[:16]} for r in rows]


def _clean_blocks(blocks):
    out = []
    for b in blocks or []:
        name = b.get("web_template")
        if not name or not frappe.db.exists("Web Template", name):
            continue
        out.append({"web_template": name, "values": b.get("values") if isinstance(b.get("values"), dict) else {},
                    "hide": int(b.get("hide") or 0), "shade": int(b.get("shade") or 0),
                    "section_id": re.sub(r"[^A-Za-z0-9_-]", "", b.get("section_id") or "")[:60],
                    "css_class": re.sub(r"[^A-Za-z0-9_ -]", "", b.get("css_class") or "")[:120]})
    return out


@frappe.whitelist()
def render(block, idx=0):
    """HTML of one section, exactly as the public page would show it. Used for live preview while editing."""
    _guard()
    block = json.loads(block) if isinstance(block, str) else block
    clean = _clean_blocks([block])
    if not clean:
        frappe.throw(_("Unknown section"))
    return render_block(clean[0], edit=True, idx=int(idx or 0))


@frappe.whitelist(methods=["POST"])
def save_draft(page, data):
    _guard()
    data = json.loads(data) if isinstance(data, str) else data
    doc = frappe.get_doc("Web Page", page)
    draft = {"title": (data.get("title") or doc.title).strip()[:140],
             "meta_description": (data.get("meta_description") or "").strip()[:300], "blocks": _clean_blocks(data.get("blocks"))}
    frappe.db.set_value("Web Page", page, "pcpb_draft", json.dumps(draft))
    doc.reload()
    _back_to_working_state(doc)
    frappe.db.commit()
    return _page_state(frappe.get_doc("Web Page", page))


def _back_to_working_state(doc):
    """A live page that gets new draft changes goes back into the workflow, if the workflow offers the user such a step."""
    wf = _workflow(doc)
    if not wf or wf["state"] not in wf["live_states"]:
        return
    from frappe.model.workflow import apply_workflow, get_transitions
    for t in get_transitions(doc):
        if t.get("next_state") not in wf["live_states"]:
            w = frappe.get_cached_doc("Workflow", wf["name"])
            target = next((s for s in w.states if s.state == t.get("next_state")), None)
            if target is not None and not target.update_field:
                apply_workflow(doc, t.get("action"))
                return


@frappe.whitelist(methods=["POST"])
def workflow_action(page, action):
    """Run one step of the Web Page workflow (Submit for Review, Approve, Publish ...)."""
    _guard()
    from frappe.model.workflow import apply_workflow
    doc = frappe.get_doc("Web Page", page)
    apply_workflow(doc, action)
    frappe.db.commit()
    frappe.website.utils.clear_cache(doc.route)
    return _page_state(frappe.get_doc("Web Page", page))


@frappe.whitelist(methods=["POST"])
def publish_now(page):
    """Only used when no workflow is active on Web Page: a Website Manager publishes the draft directly."""
    _guard(manager=True)
    from frappe.model.workflow import get_workflow_name
    if get_workflow_name("Web Page"):
        frappe.throw(_("Publishing follows the Web Page workflow. Use the workflow buttons."))
    doc = frappe.get_doc("Web Page", page)
    apply_draft(doc)
    doc.published = 1
    doc.save()
    frappe.db.commit()
    return _page_state(doc)


@frappe.whitelist(methods=["POST"])
def discard_draft(page):
    _guard()
    frappe.db.set_value("Web Page", page, "pcpb_draft", "")
    frappe.db.commit()
    return _page_state(frappe.get_doc("Web Page", page))


def _presets():
    path = frappe.get_app_path("pcpb_website", "page_presets.json")
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


@frappe.whitelist()
def presets():
    _guard()
    return [{"key": k, "label": v.get("label") or k, "description": v.get("description") or ""} for k, v in _presets().items()]


@frappe.whitelist(methods=["POST"])
def create_page(title, route=None, preset="blank", add_to_menu=0, menu_parent=None):
    _guard()
    title = (title or "").strip()
    if not title:
        frappe.throw(_("Give the page a title"))
    route = re.sub(r"[^a-z0-9/-]+", "-", (route or title).strip().lower()).strip("-/")
    if not route:
        frappe.throw(_("Give the page an address"))
    if frappe.db.exists("Web Page", {"route": route}):
        frappe.throw(_("A page already uses the address /{0}").format(route))
    blocks = []
    for b in (_presets().get(preset) or {}).get("blocks") or []:
        vals = json.loads(json.dumps(b.get("values") or {}).replace("{{title}}", title.replace('"', "'")))
        blocks.append({"web_template": b["web_template"], "values": vals, "shade": b.get("shade", 0)})
    doc = frappe.get_doc({"doctype": "Web Page", "title": title, "route": route, "published": 0, "content_type": "Page Builder",
                          "pcpb_draft": json.dumps({"title": title, "meta_description": "", "blocks": _clean_blocks(blocks)})})
    doc.insert()
    if int(add_to_menu or 0) and is_manager():
        ws = frappe.get_doc("Website Settings")
        ws.append("top_bar_items", {"label": title, "url": "/" + route, "parent_label": menu_parent or "", "right": 0})
        ws.save(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "route": doc.route}


@frappe.whitelist(methods=["POST"])
def duplicate_page(page, title):
    """A copy of a page as a new unpublished draft, with all its sections."""
    _guard()
    title = (title or "").strip()
    if not title:
        frappe.throw(_("Give the copy a title"))
    src = frappe.get_doc("Web Page", page)
    blocks = (draft_of(src) or {}).get("blocks") or live_blocks(src)
    base = re.sub(r"[^a-z0-9/-]+", "-", title.lower()).strip("-/") or "page"
    route, n = base, 1
    while frappe.db.exists("Web Page", {"route": route}):
        n += 1
        route = f"{base}-{n}"
    doc = frappe.get_doc({"doctype": "Web Page", "title": title, "route": route, "published": 0, "content_type": "Page Builder",
                          "pcpb_draft": json.dumps({"title": title, "meta_description": src.meta_description or "", "blocks": _clean_blocks(blocks)})})
    doc.insert()
    frappe.db.commit()
    return {"name": doc.name, "route": doc.route}


@frappe.whitelist(methods=["POST"])
def save_page_settings(page, route=None, make_home=0):
    """Change a page's address or make it the home page. Managers only, because links elsewhere may depend on it."""
    _guard(manager=True)
    doc = frappe.get_doc("Web Page", page)
    old = doc.route
    if route is not None:
        new = re.sub(r"[^a-z0-9/-]+", "-", route.strip().lower()).strip("-/")
        if new and new != old:
            if frappe.db.exists("Web Page", {"route": new, "name": ["!=", page]}):
                frappe.throw(_("A page already uses the address /{0}").format(new))
            frappe.db.set_value("Web Page", page, "route", new)
            ws = frappe.get_doc("Website Settings")
            ws.append("route_redirects", {"source": old, "target": "/" + new})
            if (ws.home_page or "") == old:
                ws.home_page = new
            ws.save(ignore_permissions=True)
    if int(make_home or 0):
        frappe.db.set_single_value("Website Settings", "home_page", frappe.db.get_value("Web Page", page, "route"))
    frappe.db.commit()
    frappe.clear_cache()
    return _page_state(frappe.get_doc("Web Page", page))


# ------------------------------------------------------------------ getting started
README_URL = "https://github.com/muthukiaowen/PCPB-Website#readme"


ONBOARDING = "PCPB Website Onboarding"


def _detected():
    """Steps the site can see are done, whatever anyone ticked. Keyed by Onboarding Step name."""
    from pcpb_website import remote
    s = site()
    count = lambda dt, flt=None: frappe.db.count(dt, flt or {}) if frappe.db.exists("DocType", dt) else 0
    staff = frappe.get_all("Has Role", filters={"role": ["in", ["Website Content Editor", "Website Content Approver", "Website Publisher"]],
                                                "parenttype": "User"}, pluck="parent", distinct=True)
    edited = frappe.db.sql("select count(*) from `tabWeb Page` where modified > creation + interval 1 minute")[0][0]
    return {
        "PCPB Website Identity": bool(s.get("logo")),
        "PCPB Website Integration": bool(remote.fetch("link_status", ttl=0)) if remote.on() else None,
        "PCPB Website Pages": bool(edited),
        "PCPB Website Roles": bool(staff),
        "PCPB Website Registers": bool(count("PCPB Register", {"published": 1})) or remote.on(),
        "PCPB Website Posts": bool(count("PCPB Post", {"published": 1})),
    }


def _step_target(step):
    """Where a step's button goes when it is pressed in the website builder."""
    if step.action in ("Update Settings", "Create Entry") and step.reference_document:
        route = "/desk/" + frappe.scrub(step.reference_document).replace("_", "-")
        return route + ("/new" if step.action == "Create Entry" else "")
    path = (step.path or "").strip()
    if not path:
        return ""
    return path if path.startswith(("/", "http")) else "/desk/" + path


@frappe.whitelist()
def getting_started():
    """The set-up guide. It is the standard Module Onboarding record, so the Desk and the builder show the same
    steps, and an administrator edits the wording in Desk > Onboarding Step."""
    _guard()
    from pcpb_website import remote
    out = {"title": "Set up the PCPB website", "steps": [], "mode": remote.mode(), "readme": README_URL, "guide": "/website-guide",
           "is_manager": is_manager(), "edit_url": f"/desk/module-onboarding/{frappe.utils.quote(ONBOARDING)}"}
    if not frappe.db.exists("Module Onboarding", ONBOARDING):
        return out
    doc = frappe.get_doc("Module Onboarding", ONBOARDING)
    out["title"] = doc.title or out["title"]
    seen = _detected()
    for row in doc.steps:
        if not frappe.db.exists("Onboarding Step", row.step):
            continue
        st = frappe.get_doc("Onboarding Step", row.step)
        auto = seen.get(st.name)
        out["steps"].append({
            "name": st.name, "title": st.title, "description": frappe.utils.md_to_html(st.description or "") or "",
            "label": st.action_label or st.action, "target": _step_target(st), "optional": int(row.is_optional or 0),
            "done": bool(st.is_complete) or bool(auto), "skipped": bool(st.is_skipped) and not auto, "video": st.intro_video_url or "",
        })
    return out


@frappe.whitelist(methods=["POST"])
def guide_step(step, state):
    """Mark a step done, skipped or open again. Uses the standard Onboarding Step flags."""
    _guard(manager=True)
    if not frappe.db.exists("Onboarding Step", step) or state not in ("done", "skipped", "open"):
        frappe.throw(_("Unknown step"))
    frappe.db.set_value("Onboarding Step", step, {"is_complete": int(state == "done"), "is_skipped": int(state == "skipped")})
    frappe.db.commit()
    return getting_started()


# ------------------------------------------------------------------ logo and name
IDENTITY_FIELDS = ["site_name", "tagline", "parent_body", "logo", "logo_alt", "footer_logo", "favicon"]


@frappe.whitelist()
def get_identity():
    _guard(manager=True)
    s = frappe.get_doc("PCPB Website Settings")
    out = {f: s.get(f) or "" for f in IDENTITY_FIELDS if f != "favicon"}
    out["favicon"] = frappe.db.get_single_value("Website Settings", "favicon") or ""
    out["logo_on_desk"] = cint(s.get("logo_on_desk"))
    return out


@frappe.whitelist(methods=["POST"])
def save_identity(values):
    """Logo, organisation name and browser icon. The browser icon is the standard Website Settings favicon."""
    _guard(manager=True)
    values = json.loads(values) if isinstance(values, str) else values
    s = frappe.get_doc("PCPB Website Settings")
    for f in IDENTITY_FIELDS:
        if f in values and f != "favicon":
            s.set(f, (values[f] or "").strip())
    if "logo_on_desk" in values:
        s.logo_on_desk = cint(values["logo_on_desk"])
    if not s.site_name:
        frappe.throw(_("The organisation name cannot be empty"))
    s.save(ignore_permissions=True)
    if "favicon" in values:
        frappe.db.set_single_value("Website Settings", "favicon", (values["favicon"] or "").strip())
    frappe.db.commit()
    frappe.clear_cache()
    return get_identity()


# ------------------------------------------------------------------ theme
@frappe.whitelist()
def preview_theme(values):
    _guard(manager=True)
    values = json.loads(values) if isinstance(values, str) else values
    return theme_vars(frappe._dict({k: values.get(k) for k in THEME_FIELDS}))


@frappe.whitelist(methods=["POST"])
def save_theme(values):
    _guard(manager=True)
    values = json.loads(values) if isinstance(values, str) else values
    s = frappe.get_doc("PCPB Website Settings")
    for f in THEME_FIELDS:
        if f in values:
            s.set(f, values[f])
    s.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
    return theme_vars()


# ------------------------------------------------------------------ menu (standard Website Settings tables)
@frappe.whitelist()
def get_menu():
    _guard(manager=True)
    ws = frappe.get_doc("Website Settings")
    row = lambda r: {"label": r.label, "url": r.url or "", "parent_label": r.parent_label or "",
                     "right": int(r.get("right") or 0), "open_in_new_tab": int(r.get("open_in_new_tab") or 0)}
    return {"top": [row(r) for r in ws.top_bar_items], "footer": [row(r) for r in ws.footer_items],
            "redirects": [{"source": r.source, "target": r.target} for r in ws.route_redirects]}


@frappe.whitelist(methods=["POST"])
def save_menu(data):
    _guard(manager=True)
    data = json.loads(data) if isinstance(data, str) else data
    ws = frappe.get_doc("Website Settings")
    for key, table in (("top", "top_bar_items"), ("footer", "footer_items")):
        if key not in data:
            continue
        ws.set(table, [])
        for r in data[key]:
            if not (r.get("label") or "").strip():
                continue
            ws.append(table, {"label": r["label"].strip(), "url": (r.get("url") or "").strip(),
                              "parent_label": (r.get("parent_label") or "").strip(), "right": 0,
                              "open_in_new_tab": int(r.get("open_in_new_tab") or 0)})
    if "redirects" in data:
        ws.set("route_redirects", [])
        for r in data["redirects"]:
            src, tgt = (r.get("source") or "").strip().strip("/"), (r.get("target") or "").strip()
            if src and tgt:
                ws.append("route_redirects", {"source": src, "target": tgt})
    ws.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
    return get_menu()


# ------------------------------------------------------------------ pickers
@frappe.whitelist()
def link_options(doctype, txt=""):
    """Choices for a Link field of a section (which register, which web form ...)."""
    _guard()
    allowed = {f["options"] for t in _library() for f in t["fields"] if f["fieldtype"] == "Link" and f["options"]}
    if doctype not in allowed:
        frappe.throw(_("Not allowed"), frappe.PermissionError)
    meta = frappe.get_meta(doctype)
    title = meta.title_field if meta.title_field and meta.title_field != "name" else None
    fields = ["name"] + ([title] if title else [])
    filters = {}
    if txt:
        filters = {(title or "name"): ["like", f"%{txt}%"]}
    rows = frappe.get_all(doctype, filters=filters, fields=fields, limit=50, order_by="modified desc")
    return [{"value": r.name, "label": (r.get(title) if title else None) or r.name} for r in rows]


@frappe.whitelist()
def link_targets():
    """Places a button or menu item can point to: pages, registers, and the fixed areas of the site."""
    _guard()
    out = [{"label": p["title"], "url": "/" + (p["route"] or ""), "group": "Pages"} for p in pages()]
    for r in frappe.get_all("PCPB Register", filters={"published": 1}, fields=["name", "title"]):
        out.append({"label": r.title, "url": f"/registers/{r.name}", "group": "Registers"})
    for w in frappe.get_all("Web Form", filters={"published": 1}, fields=["title", "route"]):
        out.append({"label": w.title, "url": "/" + (w.route or ""), "group": "Forms"})
    from pcpb_website.utils import portals
    pt = portals()
    if pt.customer:
        out += [{"label": f"{pt.customer.name}: sign in", "url": pt.customer.sign_in, "group": "Portals"},
                {"label": f"{pt.customer.name}: create an account", "url": pt.customer.sign_up, "group": "Portals"},
                {"label": f"{pt.customer.name}: home", "url": pt.customer.home, "group": "Portals"}]
        if pt.customer.verify:
            out.append({"label": "Verify a certificate", "url": pt.customer.verify, "group": "Portals"})
    if pt.supplier:
        out.append({"label": f"{pt.supplier.name}: sign in", "url": pt.supplier.sign_in, "group": "Portals"})
    out.append({"label": "Search", "url": "/search", "group": "Other"})
    return out
