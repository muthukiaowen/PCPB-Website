"""Sets up a working PCPB website on install, and keeps the structure in place on every migrate.

Rule: this file only creates what is missing. Once staff change a page, a menu or a setting, it is never
overwritten. Everything created here is ordinary data that staff edit in the builder or the Desk.
"""
import json

import frappe

from pcpb_website.utils import DEFAULT_LABELS

ROLES = ["Website Content Editor", "Website Content Approver", "Website Publisher"]
E, A, P, M = "Website Content Editor", "Website Content Approver", "Website Publisher", "Website Manager"


def ensure_roles():
    for r in ROLES:
        if not frappe.db.exists("Role", r):
            frappe.get_doc({"doctype": "Role", "role_name": r, "desk_access": 1}).insert(ignore_permissions=True)
    # the role of the API user a separately hosted website signs in as; it opens nothing in the Desk
    if not frappe.db.exists("Role", "PCPB Website Integration"):
        frappe.get_doc({"doctype": "Role", "role_name": "PCPB Website Integration", "desk_access": 0}).insert(ignore_permissions=True)
    frappe.db.commit()


def after_install():
    after_migrate()


def after_migrate():
    ensure_roles()
    for fn in (custom_fields, permissions, workflows, labels, settings_defaults, integration_defaults, register_groups, registers, destinations,
               service_profiles, starter_site, help_articles, desk_entry, workspace_onboarding, desk_logo):
        try:
            fn()
            frappe.db.commit()
        except Exception:
            frappe.db.rollback()
            frappe.log_error(title=f"PCPB Website setup step failed: {fn.__name__}")
    frappe.clear_cache()


def desk_logo():
    """A migrate reloads the standard Desk icon, so the uploaded logo is put back on it here."""
    from pcpb_website.pcpb_website.doctype.pcpb_website_settings.pcpb_website_settings import sync_desk_logo
    sync_desk_logo()


# ---------------------------------------------------------------- structure
def custom_fields():
    """One addition to the standard Web Page: the draft the builder saves until the page is published."""
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields({
        "Web Page": [
            {"fieldname": "pcpb_draft", "fieldtype": "Long Text", "label": "Builder Draft", "hidden": 1, "no_copy": 1, "insert_after": "page_blocks"},
        ],
    }, ignore_validate=True, update=True)


MANAGER_DOCTYPES = ["Web Page", "Web Template", "Web Form", "Website Settings", "Contact Us Settings", "About Us Settings",
                    "Help Article", "Help Category", "Onboarding Step", "Module Onboarding"]


def manager_role():
    """Website Manager is the administrator of this app. Create the role if the site lacks it and make sure it holds
    full rights on every record the website is built from. Rights are only ever added, never removed."""
    from frappe.permissions import add_permission, update_permission_property
    if not frappe.db.exists("Role", M):
        frappe.get_doc({"doctype": "Role", "role_name": M, "desk_access": 1}).insert(ignore_permissions=True)
    own = frappe.get_all("DocType", filters={"module": "PCPB Website", "istable": 0}, pluck="name")
    for dt in own + MANAGER_DOCTYPES:
        if not frappe.db.exists("DocType", dt):
            continue
        meta = frappe.get_meta(dt)
        if any(p.role == M and not p.permlevel and p.read and p.write for p in meta.permissions):
            continue
        add_permission(dt, M, 0)
        for right in ("write",) if meta.issingle else ("write", "create", "delete"):
            update_permission_property(dt, M, 0, right, 1, validate=False)


def permissions():
    """Website staff roles may create and edit standard Web Pages. Publishing is decided by the workflow."""
    from frappe.permissions import add_permission, update_permission_property
    manager_role()
    for role in ROLES:
        if not frappe.db.exists("Custom DocPerm", {"parent": "Web Page", "role": role, "permlevel": 0}):
            add_permission("Web Page", role, 0)
            for p in ("write", "create"):
                update_permission_property("Web Page", role, 0, p, 1, validate=False)


def _workflow(doctype, name, live_draft=False):
    """Approval steps as an ordinary Workflow record. PCPB can change the steps in Desk > Workflow.

    live_draft: used for Web Page, where a published page stays live while its next version is drafted."""
    if not frappe.db.exists("DocType", doctype) or frappe.db.exists("Workflow", {"document_type": doctype}):
        return
    for s in ("Draft", "In Review", "Approved", "Published", "Withdrawn"):
        if not frappe.db.exists("Workflow State", s):
            frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": s}).insert(ignore_permissions=True)
    for a in ("Submit for Review", "Send Back", "Approve", "Publish", "Withdraw", "Reopen", "Publish Directly", "Revise"):
        if not frappe.db.exists("Workflow Action Master", a):
            frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": a}).insert(ignore_permissions=True)
    # state, roles that may edit in it, value written to "published" (None = leave as is)
    off = None if live_draft else 0
    states = [("Draft", (E, M), off), ("In Review", (A, M), off), ("Approved", (P, M), off), ("Published", (P, M), 1), ("Withdrawn", (E, M), 0)]
    trans = [("Draft", "Submit for Review", "In Review", E), ("Draft", "Submit for Review", "In Review", M),
             ("In Review", "Send Back", "Draft", A), ("In Review", "Approve", "Approved", A), ("In Review", "Approve", "Approved", M),
             ("Approved", "Publish", "Published", P), ("Approved", "Publish", "Published", M), ("Approved", "Send Back", "Draft", P),
             ("Draft", "Publish Directly", "Published", M),
             ("Published", "Revise", "Draft", E), ("Published", "Revise", "Draft", M),
             ("Published", "Withdraw", "Withdrawn", P), ("Published", "Withdraw", "Withdrawn", M),
             ("Withdrawn", "Reopen", "Draft", E), ("Withdrawn", "Reopen", "Draft", M)]
    wf = frappe.get_doc({"doctype": "Workflow", "workflow_name": name, "document_type": doctype, "is_active": 1,
                         "workflow_state_field": "workflow_state", "send_email_alert": 0, "states": [], "transitions": []})
    for st, roles, pub in states:
        for role in roles:
            row = {"state": st, "doc_status": "0", "allow_edit": role}
            if pub is not None:
                row.update({"update_field": "published", "update_value": str(pub)})
            wf.append("states", row)
    for st, act, nxt, role in trans:
        wf.append("transitions", {"state": st, "action": act, "next_state": nxt, "allowed": role, "allow_self_approval": 1})
    wf.insert(ignore_permissions=True)
    if frappe.db.has_column(doctype, "workflow_state") and frappe.db.has_column(doctype, "published"):
        frappe.db.sql(f"update `tab{doctype}` set workflow_state='Published' where published=1 and ifnull(workflow_state,'')=''")
        frappe.db.sql(f"update `tab{doctype}` set workflow_state='Draft' where ifnull(published,0)=0 and ifnull(workflow_state,'')=''")


def workflows():
    _workflow("Web Page", "PCPB Web Page Publishing", live_draft=True)
    _workflow("PCPB Post", "PCPB Post Approval")
    _workflow("PCPB Leader", "PCPB Leader Approval")
    _workflow("PCPB Tender", "PCPB Tender Approval")
    _workflow("PCPB Service Profile", "PCPB Service Profile Approval")


def labels():
    """Every fixed word on the site sits in Settings > Wording, so staff can change or translate it."""
    s = frappe.get_doc("PCPB Website Settings")
    have = {r.key for r in s.get("ui_labels") or []}
    added = False
    for k, wording in DEFAULT_LABELS.items():
        if k not in have:
            s.append("ui_labels", {"key": k, "wording": wording})
            added = True
    if added:
        s.flags.ignore_mandatory = True
        s.save(ignore_permissions=True)


OFFICES = [
    ("Head Office, Nairobi", "4th Floor, PCPB Building, off Waiyaki Way, Loresho. P.O. Box 13794 - 00800, Nairobi.", "0720 480 904", "info@pcpb.go.ke"),
    ("Mt Kenya Region, Embu", "", "", "mtkenya@pcpb.go.ke"),
    ("South Rift Region, Nakuru", "", "051-2217544", "southrift@pcpb.go.ke"),
    ("Western Region, Kisumu", "", "+254110003175", "ksm@pcpb.go.ke"),
    ("Coast Region, Mtwapa (KALRO)", "", "+254708349454", "coast.region@pcpb.go.ke"),
    ("North Rift Region, Eldoret", "", "0202010020", "northrift@pcpb.go.ke"),
]
SETTING_DEFAULTS = {
    "site_name": "Pest Control Products Board",
    "tagline": "Safe, effective and responsible use of pest control products in Kenya",
    "parent_body": "State Department for Crop Development",
    "address": "4th Floor, PCPB Building, off Waiyaki Way, Loresho\nP.O. Box 13794 - 00800, Nairobi", "phone": "0720 480 904",
    "email": "info@pcpb.go.ke", "hours": "Monday to Friday, 8:00 am to 5:00 pm",
    "footer": "Regulating the manufacture, import, distribution, sale, use and disposal of pest control products in Kenya, under the Pest Control Products Act.",
    "footer_note": "Register data is provided for information. Always confirm with the Board.",
    "color_primary": "#0b5d3b", "color_dark": "#073f29", "color_accent": "#e8c55a", "color_soft": "#eef2ec", "color_bg": "#f5f7f4", "color_text": "#14221b",
    "map_lat": "-1.2650", "map_lng": "36.7590",
}


def settings_defaults():
    s = frappe.get_doc("PCPB Website Settings")
    changed = False
    for k, v in SETTING_DEFAULTS.items():
        if not s.get(k):
            s.set(k, v)
            changed = True
    # Each switch or number takes its starting value once, the first time it exists. After that whatever staff
    # choose is kept, including "off". The list of settings already started is kept in a hidden field.
    started = set((s.get("defaults_applied") or "").split(","))
    for df in s.meta.fields:
        if df.default and df.fieldtype in ("Check", "Int", "Select", "Data", "Small Text") and df.fieldname not in started:
            if not s.get(df.fieldname):
                s.set(df.fieldname, df.default)
            started.add(df.fieldname)
            changed = True
    s.defaults_applied = ",".join(sorted(x for x in started if x))
    if not s.get("offices"):
        for name, addr, tel, mail in OFFICES:
            s.append("offices", {"office_name": name, "address": addr, "phone": tel, "email": mail})
        changed = True
    if changed:
        s.save(ignore_permissions=True)


# ---------------------------------------------------------------- integration settings
def integration_defaults():
    """Deployment mode and the portal list. Runs on every migrate but only fills what is still empty."""
    from pcpb_website.pcpb_website.doctype.pcpb_website_integration.pcpb_website_integration import ERP, SINGLE
    doc = frappe.get_doc("PCPB Website Integration")
    stored = {r[0] for r in frappe.db.sql("select field from tabSingles where doctype='PCPB Website Integration'")}
    changed = False
    if "deployment_mode" not in stored:
        # An ERP server says so before install:  bench --site <site> set-config pcpb_website_role provider
        doc.deployment_mode = ERP if frappe.conf.get("pcpb_website_role") == "provider" else SINGLE
        doc.cache_seconds, doc.request_timeout = 120, 10
        changed = True
    if not doc.get("portals"):
        doc.append("portals", {"portal_name": "Customer Portal", "audience": "Customers and applicants", "enabled": 1, "show_in_header": 1,
                               "sign_in_path": "/login", "sign_up_path": "/signup", "home_path": "/portal", "verify_path": "/verify"})
        # listed so it is seen and can be switched on once the supplier portal's address and pages are confirmed
        doc.append("portals", {"portal_name": "Supplier Portal", "audience": "Suppliers", "enabled": 0, "show_in_header": 1,
                               "sign_in_path": "/login", "sign_up_path": "/signup", "home_path": "/portal"})
        changed = True
    if changed:
        doc.flags.ignore_mandatory = True
        doc.save(ignore_permissions=True)


# ---------------------------------------------------------------- registers
GROUPS = [
    ("Registered products", "Products authorised for sale and use in Kenya", 10),
    ("Licensed premises", "Premises inspected and licensed by the Board", 20),
    ("Special authorisations", "Emergency use, temporary registrations and field trials", 30),
    ("Restrictions and prohibitions", "Restricted, withdrawn and banned products and active ingredients", 40),
]
# fieldname, label, in_list, in_detail, searchable, filterable
PRODUCT_FIELDS = [
    ("registration_no", "Registration Number", 1, 1, 1, 0),
    ("trade_name", "Trade Name", 1, 1, 1, 0),
    ("product_name", "Product Name", 1, 1, 1, 0),
    ("actives.active_ingredient", "Active Ingredient", 1, 1, 1, 0),
    ("product_category", "Category", 1, 1, 0, 1),
    ("category", "Category", 1, 1, 0, 1),
    ("product_function", "Function", 0, 1, 0, 1),
    ("formulation_type", "Formulation", 0, 1, 0, 0),
    ("who_hazard_class", "WHO Hazard Class", 0, 1, 0, 1),
    ("registration_purpose", "Registration Purpose", 0, 1, 0, 0),
    ("registrant.party_name", "Registrant", 1, 1, 1, 0),
    ("applicant", "Registrant", 1, 1, 1, 0),
    ("local_agent.party_name", "Local Agent", 0, 1, 1, 0),
    ("manufacturer.party_name", "Manufacturer", 0, 1, 0, 0),
    ("approved_uses.crop", "Crop", 0, 1, 1, 0),
    ("approved_uses.pest", "Pest", 0, 1, 0, 0),
    ("certificate_number", "Certificate Number", 0, 1, 1, 0),
    ("registration_date", "Registered On", 0, 1, 0, 0),
    ("valid_to", "Valid Until", 1, 1, 0, 0),
]
PREMISES_FIELDS = [
    ("premises_name", "Premises Name", 1, 1, 1, 0),
    ("owner_party", "Owner", 1, 1, 1, 0),
    ("county", "County", 1, 1, 0, 1),
    ("town", "Town", 1, 1, 1, 0),
    ("categories.premises_category", "Premises Category", 0, 1, 0, 0),
    ("certificate_no", "Certificate Number", 1, 1, 1, 0),
    ("licence_no", "Licence Number", 1, 1, 1, 0),
    ("certified_year", "Certified Year", 0, 1, 0, 1),
    ("certified_to", "Valid Until", 1, 1, 0, 0),
]
# slug, title, group, description, icon, kind, doctype, filter, title_field, fields, published, order
REGISTERS = [
    ("registered-products", "Registered pest control products", "Registered products",
     "Pest control products registered for sale and use in Kenya.", "leaf", "Standard", "Product", {"status": "Registered"},
     "trade_name", PRODUCT_FIELDS, 1, 10),
    ("temporary-registrations", "Temporary registrations", "Special authorisations",
     "Products holding a temporary registration.", "clock", "Standard", "Product", {"status": "Temporary"}, "trade_name", PRODUCT_FIELDS, 0, 20),
    ("licensed-premises", "Licensed premises", "Licensed premises",
     "Premises inspected and licensed to manufacture, store or sell pest control products.", "building", "Standard", "Premises",
     {"status": "Active", "has_certificate": 1, "certified_to": [">=", "__today__"]}, "premises_name", PREMISES_FIELDS, 1, 30),
]


def register_groups():
    for name, desc, order in GROUPS:
        if not frappe.db.exists("PCPB Register Group", name):
            frappe.get_doc({"doctype": "PCPB Register Group", "group_name": name, "description": desc,
                            "display_order": order}).insert(ignore_permissions=True)


def registers():
    """Starting registers. Only fields that really exist on the ERP record type are listed, so nothing is guessed."""
    if frappe.db.count("PCPB Register"):
        return
    from pcpb_website.api import _usable
    for slug, title, group, desc, icon, kind, dt, flt, title_field, fields, published, order in REGISTERS:
        if not frappe.db.exists("DocType", dt):
            continue
        meta = frappe.get_meta(dt)
        flt = {k: v for k, v in flt.items() if meta.has_field(k)}
        doc = frappe.get_doc({"doctype": "PCPB Register", "slug": slug, "title": title, "register_group": group,
                              "description": desc, "icon": icon, "status_kind": kind, "source_doctype": dt,
                              "public_filter": json.dumps(flt) if flt else "", "published": published if flt else 0, "display_order": order,
                              "title_field": title_field if meta.has_field(title_field) else "", "page_length": 25, "allow_export": 1,
                              "ingredient_field": "actives.active_ingredient" if _usable(dt, "actives.active_ingredient") else ""})
        for fn, label, lst, det, srch, flt_ in fields:
            if _usable(dt, fn):
                doc.append("fields", {"fieldname": fn, "public": 1, "label": label, "in_list": lst, "in_detail": det,
                                      "searchable": srch, "filterable": flt_})
        if doc.fields:
            doc.insert(ignore_permissions=True)
    frappe.db.delete("PCPB Register Field", {"parenttype": "PCPB Register Settings"})


# ---------------------------------------------------------------- services catalogue
SYSTEMS = [
    ("PCPB Service Portal", "PCPB's online service application portal (the ERP portal).", "", 1, 0, 1),
    ("OPRS", "Online Pesticides Registration System (legacy). Address taken from the current pcpb.go.ke site; confirm.", "https://oprs.pcpb.go.ke/", 0, 1, 0),
    ("KenTrade TFP", "Kenya Trade Facilitation Platform: import and export permits. Address taken from the current site; confirm.", "https://tfp.kenyatradenet.go.ke/TFBSEW/cusLogin/signin.cl", 0, 1, 0),
    ("eCitizen", "Government of Kenya digital services (PCPB eCitizen). Address taken from the current site; confirm.", "https://pcpb.ecitizen.go.ke/", 0, 1, 0),
    ("External information page", "Information hosted outside this website.", "", 0, 1, 0),
]


def destinations():
    for name, desc, url, portal, ext, ver in SYSTEMS:
        if not frappe.db.exists("PCPB Destination System", name):
            frappe.get_doc({"doctype": "PCPB Destination System", "system_name": name, "description": desc, "base_url": url,
                            "is_portal": portal, "external": ext, "verified": ver}).insert(ignore_permissions=True)


def service_profiles():
    """One profile per portal Service so staff can enrich how it is described. The service itself stays in the ERP."""
    if not frappe.db.exists("DocType", "Service"):
        return
    for r in frappe.get_all("Service", fields=["name", "description"]):
        if frappe.db.exists("PCPB Service Profile", r.name):
            continue
        d = frappe.get_doc({"doctype": "PCPB Service Profile", "service": r.name, "published": 1, "application_method": "Online",
                            "destination_system": "PCPB Service Portal", "short": (r.description or "")[:180]})
        d.insert(ignore_permissions=True)
        if frappe.db.has_column("PCPB Service Profile", "workflow_state"):
            frappe.db.set_value("PCPB Service Profile", d.name, "workflow_state", "Published")


# ---------------------------------------------------------------- starter website (pages, menu, addresses)
def _starter():
    with open(frappe.get_app_path("pcpb_website", "starter_site.json")) as f:
        return json.load(f)


def _make_page(p):
    if frappe.db.exists("Web Page", {"route": p["route"]}):
        return
    doc = frappe.get_doc({"doctype": "Web Page", "title": p["title"], "route": p["route"],
                          "published": 1, "content_type": "Page Builder", "meta_description": p.get("description") or ""})
    for b in p["blocks"]:
        if not frappe.db.exists("Web Template", b["web_template"]):
            continue
        doc.append("page_blocks", {"web_template": b["web_template"], "web_template_values": json.dumps(b.get("values") or {}),
                                   "add_shade": int(b.get("shade") or 0),
                                   "add_container": 0, "add_top_padding": 0, "add_bottom_padding": 0})
    doc.insert(ignore_permissions=True)
    if frappe.db.has_column("Web Page", "workflow_state"):
        # seeded pages start life already published; later changes go through the workflow
        frappe.db.set_value("Web Page", doc.name, {"workflow_state": "Published", "published": 1}, update_modified=False)


def starter_site():
    """Runs once. Builds the first set of pages from sections, the menu, the footer and the address redirects."""
    s = frappe.get_doc("PCPB Website Settings")
    if int(s.get("builder_seeded") or 0):
        return
    from pcpb_website import remote
    if remote.is_provider():
        return  # an ERP server shows no public website; its pages, menu and home page are left alone
    data = _starter()
    for p in data["pages"]:
        _make_page(p)

    ws = frappe.get_doc("Website Settings")
    ws.set("top_bar_items", [])
    for label, url, parent in data["menu"]:
        ws.append("top_bar_items", {"label": label, "url": url, "parent_label": parent, "right": 0})
    ws.set("footer_items", [])
    for label, url, parent in data["footer"]:
        ws.append("footer_items", {"label": label, "url": url, "parent_label": parent, "right": 0})
    have = {r.source for r in ws.get("route_redirects") or []}
    for src, tgt in data["redirects"]:
        if src not in have:
            ws.append("route_redirects", {"source": src, "target": tgt})
    if (ws.home_page or "") in ("", "home", "login", "site", "index"):
        ws.home_page = "site"
    ws.save(ignore_permissions=True)

    # the standard Frappe contact form (/contact) is the "Send us a message" form; messages go to Settings > Contact Us Settings
    try:
        cu = frappe.get_doc("Contact Us Settings")
        if cu.is_disabled:
            cu.is_disabled = 0
            cu.query_options = cu.query_options or "General enquiry\nReport a suspect product\nProduct registration\nPremises licence\nComplaint or compliment"
            cu.save(ignore_permissions=True)
    except Exception:
        frappe.log_error(title="PCPB Website: contact form not enabled")

    if not s.get("ticker_items"):
        for tag, text, url in data["ticker"]:
            s.append("ticker_items", {"tag": tag, "text": text, "url": url})
    s.builder_seeded = 1
    s.defaults_loaded = 1
    s.save(ignore_permissions=True)


def desk_entry():
    """Workspace so PCPB Website sits next to Website in the Desk. Best effort; never blocks migrate."""
    if not frappe.db.exists("DocType", "Workspace"):
        return
    shortcuts = [("PCPB Website Settings", "Settings and theme"), ("Web Page", "Pages"), ("PCPB Post", "News and notices"),
                 ("PCPB Tender", "Tenders"), ("PCPB Leader", "Leadership"), ("PCPB Document", "Documents"),
                 ("PCPB Register", "Registers"), ("PCPB Service Profile", "Service descriptions"), ("Web Form", "Forms"),
                 ("Web Template", "Section designs")]
    if frappe.db.exists("Workspace", "PCPB Website"):
        ws = frappe.get_doc("Workspace", "PCPB Website")
        if any(sc.link_to == "Web Page" for sc in ws.shortcuts):
            return
        frappe.delete_doc("Workspace", "PCPB Website", force=1, ignore_permissions=True)
    meta = frappe.get_meta("Workspace")
    vals = {"doctype": "Workspace", "name": "PCPB Website", "label": "PCPB Website", "title": "PCPB Website",
            "module": "PCPB Website", "public": 1, "icon": "globe", "app": "pcpb_website", "for_user": ""}
    vals = {k: v for k, v in vals.items() if k in ("doctype", "name") or meta.has_field(k)}
    blocks = [{"id": "hb", "type": "shortcut", "data": {"shortcut_name": "Open the page builder", "col": 3}},
              {"id": "hw", "type": "shortcut", "data": {"shortcut_name": "Open website", "col": 3}}]
    blocks += [{"id": f"h{i}", "type": "shortcut", "data": {"shortcut_name": lbl, "col": 3}} for i, (_, lbl) in enumerate(shortcuts)]
    if meta.has_field("content"):
        vals["content"] = json.dumps(blocks)
    doc = frappe.get_doc(vals)
    doc.append("shortcuts", {"label": "Open the page builder", "type": "URL", "url": "/page-builder"})
    doc.append("shortcuts", {"label": "Open website", "type": "URL", "url": "/"})
    for dt, lbl in shortcuts:
        if frappe.db.exists("DocType", dt):
            doc.append("shortcuts", {"label": lbl, "type": "DocType", "link_to": dt, "doc_view": "List"})
    doc.insert(ignore_permissions=True)


def workspace_onboarding():
    """Show the standard set-up guide at the top of the PCPB Website workspace."""
    name = "PCPB Website Onboarding"
    if not (frappe.db.exists("Workspace", "PCPB Website") and frappe.db.exists("Module Onboarding", name)):
        return
    ws = frappe.get_doc("Workspace", "PCPB Website")
    if not ws.meta.has_field("module_onboarding"):
        return
    try:
        blocks = json.loads(ws.content or "[]")
    except Exception:
        blocks = []
    if ws.module_onboarding == name and any(b.get("type") == "onboarding" for b in blocks):
        return
    blocks = [b for b in blocks if b.get("type") != "onboarding"]
    blocks.insert(0, {"id": "pcpb-onboarding", "type": "onboarding", "data": {"onboarding_name": name, "col": 12}})
    ws.module_onboarding = name
    ws.content = json.dumps(blocks)
    ws.save(ignore_permissions=True)


# ---------------------------------------------------------------- administrator guide (standard Help Articles)
HELP_CATEGORY = "PCPB Website Administration"
HELP_ARTICLES = [("Read me: what this app is and how to install it", "README.md"), ("Administrator guide", "docs/ADMIN_GUIDE.md"), ("Hosting, ERP API and portals", "docs/HOSTING.md"),
                 ("Editing and publishing pages (for content staff)", "docs/EDITOR_GUIDE.md")]


def help_articles():
    """The guide is kept as standard Help Articles so an administrator can edit it in the Desk. They are created
    once from the files in docs/ and left unpublished, so they are shown to website staff only (/website-guide)."""
    import os
    if not frappe.db.exists("DocType", "Help Article"):
        return
    if not frappe.db.exists("Help Category", HELP_CATEGORY):
        frappe.get_doc({"doctype": "Help Category", "category_name": HELP_CATEGORY,
                        "category_description": "How the PCPB website is set up and administered", "published": 0}).insert(ignore_permissions=True)
    s = frappe.get_doc("PCPB Website Settings")
    done = set((s.get("help_seeded") or "").split("|"))
    root = os.path.dirname(frappe.get_app_path("pcpb_website"))
    for title, rel in HELP_ARTICLES:
        path = os.path.join(root, rel)
        if title in done or not os.path.exists(path) or frappe.db.exists("Help Article", {"title": title, "category": HELP_CATEGORY}):
            continue
        with open(path) as f:
            text = f.read()
        text = "\n".join(text.split("\n")[1:]) if text.startswith("# ") else text  # the title is the article title
        frappe.get_doc({"doctype": "Help Article", "title": title, "category": HELP_CATEGORY, "published": 0, "author": "PCPB ICT",
                        "level": "Expert" if "Administrator" in title or "Hosting" in title else "Beginner",
                        "content": frappe.utils.md_to_html(text)}).insert(ignore_permissions=True)
        done.add(title)
    frappe.db.set_single_value("PCPB Website Settings", "help_seeded", "|".join(sorted(x for x in done if x)))


# ---------------------------------------------------------------- sample content (test sites only)
def seed_demo():
    """bench --site <site> execute pcpb_website.install.seed_demo   Adds a few sample records so a test site has
    something to show. Never run on the live site."""
    today = frappe.utils.nowdate()
    if not frappe.db.count("PCPB Post", {"published": 1}):
        for title, typ, summary, tick in [
            ("Pesticide review: products withdrawn and restricted", "Notice", "Outcome of the review of pest control products. Sample text for testing.", 1),
            ("Annual stakeholders forum", "News", "The Board met registrants, agro-dealers and county officers. Sample text for testing.", 0),
            ("Safe use of pesticides: always read the label", "Safety Alert", "Use protective clothing and follow the label. Sample text for testing.", 1)]:
            d = frappe.get_doc({"doctype": "PCPB Post", "title": title, "post_type": typ, "summary": summary,
                                "body": f"<p>{summary}</p>", "publish_date": today, "published": 1, "show_in_ticker": tick})
            d.insert(ignore_permissions=True)
            frappe.db.set_value("PCPB Post", d.name, {"published": 1, "workflow_state": "Published"})
    if not frappe.db.count("PCPB Tender"):
        for no, title, days in [("PCPB/T/001/2026-27", "Supply and delivery of laboratory reagents", 14), ("PCPB/T/002/2026-27", "Provision of security services", -5)]:
            d = frappe.get_doc({"doctype": "PCPB Tender", "title": title, "tender_no": no, "category": "Goods", "tender_status": "Open",
                                "published_on": frappe.utils.add_days(today, min(days, 0) - 14), "closing_on": frappe.utils.add_days(frappe.utils.now_datetime(), days),
                                "summary": "Sample tender for testing.", "submission_note": "Submit sealed bids to the tender box, 4th Floor.",
                                "contact_email": "procurement@pcpb.go.ke"})
            d.insert(ignore_permissions=True)
            frappe.db.set_value("PCPB Tender", d.name, {"published": 1, "workflow_state": "Published"})
    if not frappe.db.count("PCPB Leader"):
        for name, title, grp, order in [("Sample Chairperson", "Chairperson of the Board", "Board Chairperson", 1), ("Sample CEO", "Chief Executive Officer", "Chief Executive Officer", 2),
                                        ("Sample Member", "Board Member", "Board Member", 3)]:
            d = frappe.get_doc({"doctype": "PCPB Leader", "full_name": name, "official_title": title, "leader_group": grp, "tenure_status": "Current",
                                "display_order": order, "bio": "<p>Sample profile for testing.</p>"})
            d.insert(ignore_permissions=True)
            frappe.db.set_value("PCPB Leader", d.name, {"published": 1, "workflow_state": "Published"})
    if frappe.db.exists("DocType", "Job Opening") and not frappe.db.count("Job Opening"):
        try:
            if not frappe.db.exists("Designation", "Inspector"):
                frappe.get_doc({"doctype": "Designation", "designation_name": "Inspector"}).insert(ignore_permissions=True)
            company = frappe.defaults.get_global_default("company") or frappe.db.get_value("Company", {}, "name")
            if company:
                frappe.get_doc({"doctype": "Job Opening", "job_title": "Pesticide Inspector (sample)", "designation": "Inspector", "company": company,
                                "status": "Open", "publish": 1, "description": "<p>Sample vacancy for testing.</p>",
                                "closes_on": frappe.utils.add_days(today, 21)}).insert(ignore_permissions=True)
        except Exception:
            frappe.log_error(title="PCPB Website demo: job opening not created")
    frappe.db.commit()
    frappe.clear_cache()
    return "Sample content added"
