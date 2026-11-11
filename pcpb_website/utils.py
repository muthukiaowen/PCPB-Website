import frappe

DEFAULT_LABELS = {
    "supplier_portal_go": "Sign in to the supplier portal",
    "editor_bar": "You are signed in as website staff",
    "edit_this_page": "Edit this page",
    "website_builder": "Website builder",
    "open_desk": "Open Desk",
    "text_smaller": "Smaller text",
    "text_larger": "Larger text",
    "dark_mode": "Dark mode",
    "notices": "Notices",
    "pause": "Pause",
    "menu": "Menu",
    "back_to_top": "Back to top",
    "home": "Home",
    "status_check": "Product status check",
    "check": "Check",
    "check_none": "Nothing matched in the public registers. Check the spelling, or contact the Board.",
    "slider_empty": "Add slides to this slider",
    "cards_empty": "Add cards to this section",
    "image_empty": "Add a picture",
    "gallery_empty": "Pictures will appear here once they are added.",
    "records": "records",
    "open_register": "Open",
    "registers_empty": "No registers have been published yet.",
    "register_pick": "Choose a register for this section.",
    "news_none": "There are no posts in this list right now.",
    "profile": "Profile",
    "leaders_none": "Profiles will appear here once they are published.",
    "services_none": "Services will appear here once they are set up on the portal.",
    "documents_none": "There are no documents in this list right now.",
    "map": "Map",
    "offices": "Our offices",
    "form_pick": "Choose a web form for this section.",
    "expired": "Expired",
    "clear": "Clear",
    "print": "Print",
    "status": "Status",
    "page": "Page",
    "pages_and_news": "Pages, news and tenders",
    "unpublished_note": "This register is not published. Only website staff can see it.",
    "kind_note_restricted": "Products and ingredients on this list are restricted in Kenya. Conditions apply to their sale and use.",
    "kind_note_withdrawn": "Products and ingredients on this list have been withdrawn in Kenya.",
    "kind_note_banned": "Products and ingredients on this list are banned in Kenya. They must not be imported, sold or used.",
    "search": "Search",
    "all": "All",
    "next": "Next",
    "previous": "Previous",
    "tenders_title": "Tenders",
    "tenders_note": "Current and past tenders of the Pest Control Products Board.",
    "tender_open": "Open",
    "tender_closed": "Closed",
    "tender_awarded": "Awarded",
    "tender_cancelled": "Cancelled",
    "tender_no": "Tender No.",
    "tender_published": "Published",
    "tender_closes": "Closing",
    "tender_docs": "Tender documents",
    "tender_submit": "How to submit",
    "tender_award": "Award notice",
    "tender_none": "There are no tenders in this list right now.",
    "tender_view": "View tender",
    "tender_back": "All tenders",
    "tenders_open_now": "Open tenders",
    "no_results": "No records found",
    "showing": "Showing",
    "of": "of",
    "back": "Back",
    "details": "Details",
    "download": "Download",
    "downloads": "Downloads",
    "documents": "Documents",
    "category": "Category",
    "year": "Year",
    "products_title": "Registered Products",
    "premises_title": "Certified Premises",
    "register_note": "This list is drawn live from the Board's registration records.",
    "sign_in": "Sign in",
    "portal": "Applicant portal",
    "quick_links": "Quick links",
    "verify_cert": "Verify a certificate",
    "rights": "All rights reserved.",
    "latest_news": "News and notices",
    "read_more": "Read more",
    "about_board": "About the Board",
    "apply_now": "Apply now",
    "create_account": "Create an account",
    "services_note": "Applications are made on the portal. Sign in or create an account to apply; you are not charged until you submit.",
    "fee": "Fee",
    "turnaround": "Turnaround",
    "working_days": "working days",
    "services_all": "All services",
    "group:Registration": "Registration",
    "group:Premises Certification": "Premises Certification",
    "group:Laboratory": "Analytical",
    "group:Training": "Training",
    "group:Disposal": "Disposal",
    "group:Import & Export": "Import & Export",
    "group:Other": "Other",
    "services": "Online services",
    "leadership": "Leadership",
    "leadership_note": "The Board and the management of the Pest Control Products Board.",
    "careers": "Careers",
    "careers_none": "There are no open vacancies at the moment. Please check again soon.",
    "closes": "Closes",
    "location": "Duty station",
    "apply_job": "View and apply",
    "news_title": "News and notices",
    "resources": "Resources",
    "view_all": "View all",
    "registers": "Public registers",
    "quick_search": "Search registered products and certified premises",
    "search_in": "Search in",
    "skip": "Skip to content",
    "redirect_note": "You will be taken to the PCPB applicant portal to sign in and apply.",
    "eyebrow": "Statutory regulator of pest control products",
    "leaving_ext_title": "You are leaving the PCPB website",
    "leaving_portal_title": "Continuing to the PCPB Service Portal",
    "leaving_ext_body": "Applications for this service are submitted on",
    "leaving_note": "This website does not process applications. You will sign in there.",
    "continue": "Continue",
    "stay": "Stay here",
    "tbc": "To be confirmed",
    "info_only": "Information only",
    "no_apply": "The application link for this service has not been configured yet.",
    "audience": "Who can apply",
    "eligibility": "Eligibility",
    "required_docs": "Required documents",
    "steps": "How to apply",
    "legal": "Legal references",
    "faqs": "Frequently asked questions",
    "related": "Related services",
    "info_link": "More information",
    "archive": "Archive",
    "current": "Current",
    "contact_us": "Contact us",
    "featured_services": "Featured services",
    "other_leaders": "Board and management",
    "group:Board Chairperson": "Board Chairperson",
    "group:Chief Executive Officer": "Chief Executive Officer",
    "group:Board Member": "Board members",
    "group:Executive Management": "Executive management",
    "group:Department Head": "Department heads",
    "translate": "Translate",
    "translate_original": "English (original)",
    "translate_note": "Translation is automatic, provided by Google Translate. The English text is the official version.",
}


def site():
    return frappe.get_cached_doc("PCPB Website Settings")


def _labels():
    """key -> wording from Settings > Wording, cached per request."""
    cache = getattr(frappe.local, "pcpb_labels", None)
    if cache is None:
        cache = {r.key: r.wording for r in (site().get("ui_labels") or []) if r.wording}
        frappe.local.pcpb_labels = cache
    return cache


def tr(key):
    """The wording for a fixed piece of interface text. Staff can change any of it in Settings > Wording."""
    return _labels().get(key) or DEFAULT_LABELS.get(key) or key


def tr_value(value):
    """Display wording for a stored choice (for example a status), if staff set one as value:<choice>."""
    return _labels().get(f"value:{value}") or value


def lurl(path):
    """A link as typed by staff, made safe to use: site addresses always start with one slash."""
    path = (path or "").strip()
    if not path or path.startswith(("http", "mailto:", "tel:", "#")):
        return path or "#"
    return "/" + path.lstrip("/")


def translate_languages():
    """Languages offered by the Translate button, as (code, name) pairs. Empty when the button is switched off."""
    s = site()
    if not int(s.get("show_translate") or 0):
        return []
    out = []
    for line in (s.get("translate_languages") or "").splitlines():
        if ":" in line:
            code, name = line.split(":", 1)
            code = code.strip()
            if code and all(c.isalnum() or c == "-" for c in code):
                out.append((code, name.strip() or code))
    return out


# ---------------------------------------------------------------- menus (standard Website Settings)
def _tree(rows):
    top, kids = [], {}
    for r in rows:
        label = r.label
        item = frappe._dict(label=label, route=lurl(r.get("url") or "#"),
                            children=[], key=label, has_url=bool(r.get("url")))
        if r.get("parent_label"):
            kids.setdefault(r.parent_label, []).append(item)
        else:
            top.append(item)
    for t in top:
        t.children = kids.get(t.key, [])
    return top


def _ws():
    return frappe.get_cached_doc("Website Settings")


def menu_tree():
    """Header menu = standard Website Settings > Top Bar Items (left side)."""
    try:
        return _tree([r for r in (_ws().get("top_bar_items") or []) if not r.get("right")])
    except Exception:
        return []


def footer_columns():
    """Footer link columns = standard Website Settings > Footer Items. A parent label makes a column."""
    try:
        return _tree(_ws().get("footer_items") or [])
    except Exception:
        return []


def footer_links():
    return footer_columns()


# ---------------------------------------------------------------- theme
_CSS_CACHE = {}
FONTS = {
    "Inter": '"Inter","Segoe UI",system-ui,-apple-system,Roboto,"Helvetica Neue",Arial,sans-serif',
    "System": 'system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif',
    "Arial": 'Arial,"Helvetica Neue",Helvetica,sans-serif',
    "Georgia": 'Georgia,"Times New Roman",serif',
    "Verdana": 'Verdana,Geneva,sans-serif',
    "Serif": '"Source Serif 4","Iowan Old Style",Georgia,"Times New Roman",serif',
}
THEME_COLORS = {"--brand": "color_primary", "--g1": "color_dark", "--gold": "color_accent", "--surface2": "color_soft",
                "--bg": "color_bg", "--ink": "color_text"}


def _hex(v):
    v = (v or "").strip()
    return v if v.startswith("#") and len(v) in (4, 7) and all(c in "0123456789abcdefABCDEF" for c in v[1:]) else ""


def theme_vars(values=None):
    """CSS custom properties from the Theme tab. `values` lets the builder preview unsaved choices."""
    s = values or site()
    css = ""
    for var, field in THEME_COLORS.items():
        v = _hex(s.get(field))
        if v:
            css += f"{var}:{v};"
    body = FONTS.get(s.get("font_body") or "Inter")
    head = body if (s.get("font_heading") or "Serif") == "Same as body" else FONTS.get(s.get("font_heading") or "Serif", FONTS["Serif"])
    css += f"--font:{body};--serif:{head};"
    try:
        r = int(s.get("radius") if s.get("radius") not in (None, "") else 14)
        w = int(s.get("page_width") or 1220)
        css += f"--r:{max(0, min(r, 40))}px;--maxw:{max(900, min(w, 1800))}px;"
    except Exception:
        pass
    return css


def inline_css():
    """Stylesheet text placed in the page head, followed by the theme and any extra CSS from settings."""
    import os
    path = frappe.get_app_path("pcpb_website", "public", "css", "pcpb.css")
    mtime = os.path.getmtime(path)
    if _CSS_CACHE.get("m") != mtime:
        with open(path) as f:
            _CSS_CACHE["css"] = f.read()
        _CSS_CACHE["m"] = mtime
    try:
        extra = f":root{{{theme_vars()}}}\n" + (site().get("custom_css") or "").replace("</", "<\\/")
    except Exception:
        extra = ""
    return _CSS_CACHE["css"] + "\n" + extra


def asset_version():
    import os
    try:
        return str(int(os.path.getmtime(frappe.get_app_path("pcpb_website", "public", "js", "pcpb.js"))))
    except Exception:
        return "1"


# ---------------------------------------------------------------- who may edit
EDIT_ROLES = {"Website Manager", "System Manager", "Website Content Editor", "Website Content Approver", "Website Publisher"}


def can_edit(user=None):
    user = user or frappe.session.user
    if user == "Guest":
        return False
    return bool(EDIT_ROLES & set(frappe.get_roles(user)))


def is_manager(user=None):
    return bool({"Website Manager", "System Manager"} & set(frappe.get_roles(user or frappe.session.user)))


# ---------------------------------------------------------------- content readers used by sections
def _leaders_impl(groups=None, current=True):
    """Published leadership profiles, current office holders only unless current=False."""
    filters = {"published": 1}
    if current:
        filters["tenure_status"] = "Current"
    if groups:
        if isinstance(groups, str):
            groups = [g.strip() for g in groups.split(",") if g.strip()]
        filters["leader_group"] = ["in", list(groups)]
    rows = frappe.get_all("PCPB Leader", filters=filters,
                          fields=["name", "full_name", "official_title", "leader_group", "photo", "photo_alt",
                                  "bio", "email", "phone", "document", "effective_from", "effective_to", "display_order"],
                          order_by="display_order asc, full_name asc")
    today = frappe.utils.nowdate()
    out = []
    for r in rows:
        if current and r.effective_from and str(r.effective_from) > today:
            continue
        if current and r.effective_to and str(r.effective_to) < today:
            continue
        d = frappe._dict(r)
        d.title = r.official_title
        d.group_label = tr(f"group:{r.leader_group}")
        out.append(d)
    return out


def _vacancies_impl(limit=50):
    """Open, published vacancies read straight from HR (Job Opening). Nothing is copied."""
    if not frappe.db.exists("DocType", "Job Opening"):
        return []
    meta = frappe.get_meta("Job Opening")
    has = meta.has_field
    filters = {"status": "Open"} if has("status") else {}
    if has("publish"):
        filters["publish"] = 1
    want = ["name", "job_title", "designation", "department", "location", "employment_type", "posted_on", "closes_on",
            "route", "description"]
    fields = [f for f in want if f == "name" or has(f)]
    today = frappe.utils.nowdate()
    out = []
    for r in frappe.get_all("Job Opening", filters=filters, fields=fields,
                            order_by="posted_on desc" if has("posted_on") else "modified desc", limit=int(limit or 50)):
        if r.get("closes_on") and str(r.closes_on) < today:
            continue
        d = frappe._dict(r)
        d.url = f"/{r.route}" if r.get("route") else None
        d.closes_text = frappe.utils.formatdate(r.closes_on) if r.get("closes_on") else ""
        out.append(d)
    return out


def _tenders_impl(group="open", limit=50):
    """Published tenders. group: open (still accepting bids), closed (closed, awarded or cancelled), all."""
    group = (group or "open").lower()
    now = frappe.utils.now_datetime()
    rows = frappe.get_all("PCPB Tender", filters={"published": 1},
                          fields=["name", "title", "tender_no", "category", "tender_status", "published_on",
                                  "closing_on", "summary"],
                          order_by="closing_on asc" if group == "open" else "closing_on desc", limit=500)
    out = []
    for r in rows:
        closed_by_time = bool(r.closing_on and frappe.utils.get_datetime(r.closing_on) < now)
        status = "Closed" if (r.tender_status == "Open" and closed_by_time) else r.tender_status
        is_open = status == "Open"
        if group == "open" and not is_open:
            continue
        if group in ("closed", "archive") and is_open:
            continue
        d = frappe._dict(r)
        d.status = status
        d.status_label = tr("tender_" + status.lower())
        d.summary = r.summary or ""
        d.url = lurl(f"/tenders/{r.name}")
        d.closing_text = frappe.utils.format_datetime(r.closing_on, "d MMM yyyy, HH:mm") if r.closing_on else ""
        out.append(d)
    return out[: int(limit or 50)]


def _posts_impl(types="", limit=3, archive=False, ticker=False):
    """Published posts (news, notices, circulars ...), newest first. Expired ones move to the archive."""
    filters = {"published": 1}
    wanted = [t.strip() for t in (types or "").split(",") if t.strip() and t.strip().lower() != "all"]
    if wanted:
        filters["post_type"] = ["in", wanted]
    if ticker:
        filters["show_in_ticker"] = 1
    rows = frappe.get_all("PCPB Post", filters=filters,
                          fields=["name", "title", "summary", "route", "publish_date", "post_type",
                                  "expires_on", "hero_image", "hero_alt"],
                          order_by="publish_date desc, modified desc", limit=500)
    today = frappe.utils.nowdate()
    out = []
    for r in rows:
        expired = bool(r.expires_on) and str(r.expires_on) < today
        if expired != bool(archive):
            continue
        d = frappe._dict(r)
        d.url = lurl("/" + (r.route or ""))
        d.type_label = tr_value(r.post_type)
        d.date_text = frappe.utils.formatdate(r.publish_date, "d MMM yyyy") if r.publish_date else ""
        out.append(d)
        if len(out) >= int(limit or 3):
            break
    return out


def _documents_impl(category="", limit=200):
    filters = {"published": 1}
    cats = [c.strip() for c in (category or "").split(",") if c.strip() and c.strip().lower() != "all"]
    if cats:
        filters["category"] = ["in", cats]
    rows = frappe.get_all("PCPB Document", filters=filters,
                          fields=["name", "title", "category", "year", "publish_date", "file", "legacy_url"],
                          order_by="publish_date desc, modified desc", limit=int(limit or 200))
    out = []
    for r in rows:
        d = frappe._dict(r)
        d.url = r.file or r.legacy_url
        d.ext = (d.url or "").rsplit(".", 1)[-1].upper()[:4] if "." in (d.url or "") else "FILE"
        if d.url:
            out.append(d)
    return out


def _ticker_impl():
    s = site()
    if not int(s.get("show_ticker") or 0):
        return []
    out = [frappe._dict(tag=r.tag, text=r.text, url=lurl(r.url) if r.url else "")
           for r in (s.get("ticker_items") or [])]
    n = int(s.get("ticker_posts") or 0)
    if n:
        for p in _posts_impl(limit=n, ticker=True):
            out.append(frappe._dict(tag=p.type_label, text=p.title, url=p.url))
    return out


def _offices_impl():
    return [frappe._dict(name=o.office_name, address=o.address, phone=o.phone, email=o.email, lat=o.lat, lng=o.lng)
            for o in (site().get("offices") or [])]


def service_by_slug(slug):
    for s in services():
        if s.slug == slug:
            return s
    return None


def _customer_portal():
    from pcpb_website import remote
    return remote.portal("Customers and applicants") or frappe._dict(
        name=tr("portal"), base=remote.erp_base() if remote.on() else "", sign_in="/login", sign_up="/signup", home="/portal", verify="", show_in_header=1)


def _portal_base():
    """Where the customer portal lives: its own address, else the ERP when hosted separately, else this site."""
    return _customer_portal().base


def apply_url(service_name, signed_in):
    """Where Apply goes. A guest is sent to the portal sign-in and lands on the application after signing in."""
    from urllib.parse import quote
    p = _customer_portal()
    target = f"/apply?service={quote(service_name)}"
    if signed_in:
        return f"{p.base}{target}"
    return f"{p.sign_in}?redirect-to={quote(target)}"


def portal_link(path):
    """An address on the customer portal."""
    return f"{_portal_base()}{path}"


def portals():
    """Portals for the website header and for pages that point to one: customer first, then supplier."""
    from pcpb_website import remote
    out = frappe._dict(customer=remote.portal("Customers and applicants"), supplier=remote.portal("Suppliers"))
    if out.customer is None and not (remote.settings().get("portals") or []):
        out.customer = _customer_portal()  # nothing configured yet: the portal is on this site
    return out


def _services_impl():
    """The Board's online services, read live from the portal's Service records (pcpb app)."""
    profiles = _profiles()
    try:
        from pcpb.platform import portal
        rows = portal.public_services()
        shown = getattr(portal, "shown", lambda t: t)
        fees_for = getattr(portal, "fees_for", None)
    except Exception:
        rows = frappe.get_all("Service", filters={"is_active": 1, "show_on_portal": 1},
                              fields=["name", "service_name", "service_group", "description",
                                      "requires_party_role", "turnaround_days", "fee_schedule"],
                              order_by="service_group asc, service_name asc")
        shown, fees_for = (lambda t: t), None
    out = []
    for r in rows:
        total = 0
        if fees_for:
            try:
                total = sum((f.amount or 0) for f in fees_for(r.name))
            except Exception:
                total = 0
        currency = (frappe.db.get_value("Fee Schedule", r.fee_schedule, "currency") if r.fee_schedule else None) \
            or frappe.defaults.get_global_default("currency")
        name = shown(r.service_name)
        desc = shown(r.description or "")
        grp = r.service_group or "Other"
        item = frappe._dict(
            key=r.name, name=name, description=desc, group=grp, group_label=tr(f"group:{grp}") if f"group:{grp}" != tr(f"group:{grp}") else shown(grp),
            turnaround=r.turnaround_days, fee=total or None, currency=currency,
        )
        p = profiles.get(r.name)
        if p is not None and not p.published:
            continue
        _apply_profile(item, p)
        out.append(item)
    out.sort(key=lambda s: (s.order, s.name))
    return out


def _profiles():
    if not frappe.db.exists("DocType", "PCPB Service Profile"):
        return {}
    return {d.service: d for d in frappe.get_all("PCPB Service Profile", fields=["*"])}


def _lines(text):
    return [l.strip() for l in (text or "").splitlines() if l.strip()]


def _slug(name):
    return frappe.scrub(name).replace("_", "-")


def _system(name):
    if not name or not frappe.db.exists("DocType", "PCPB Destination System"):
        return None
    return frappe.db.get_value("PCPB Destination System", name, ["name", "base_url", "is_portal", "external", "verified"], as_dict=True)


def _apply_profile(item, p):
    """Attach catalogue detail and the resolved Apply action. Category never decides the destination."""
    from pcpb_website import remote
    # The website's API user is not a visitor: links it is given are the ones a guest would get.
    signed_in = frappe.session.user != "Guest" and not remote.trusted_caller()
    item.order, item.featured, item.slug = 100, 0, _slug(item.key)
    item.audience, item.eligibility, item.documents = [], [], []
    item.steps, item.legal, item.related, item.faqs = [], [], [], []
    item.fee_text, item.time_text, item.contact, item.info_url = None, None, None, None
    item.short = (item.description or "")[:180]
    item.detail, item.method = "", "Online"
    action = frappe._dict(href=apply_url(item.key, signed_in), external=False, system=tr("portal"), none=False)
    if p is not None:
        item.order, item.featured = p.display_order or 100, int(p.featured or 0)
        item.slug = p.slug or item.slug
        item.short = p.short or item.short
        item.detail = p.detail or ""
        item.audience, item.eligibility = _lines(p.audience), _lines(p.eligibility)
        item.documents, item.steps = _lines(p.documents), _lines(p.steps)
        item.legal, item.related = _lines(p.legal), _lines(p.related)
        item.fee_text, item.time_text, item.contact, item.info_url = p.fee_text, p.time_text, p.contact, p.information_url
        item.method = p.application_method or "Online"
        item.faqs = [frappe._dict(q=f.question, a=f.answer)
                     for f in frappe.get_all("PCPB FAQ", filters={"parent": p.name, "parenttype": "PCPB Service Profile"},
                                             fields=["question", "answer"], order_by="idx asc")]
        sysd = _system(p.destination_system)
        if item.method == "Information only":
            action = frappe._dict(none=True, href=None, external=False, system="")
        elif p.application_url:
            action = frappe._dict(href=p.application_url, external=p.application_url.startswith("http"),
                                  system=(sysd.name if sysd else tr("portal")), none=False)
        elif sysd and not sysd.is_portal:
            action = frappe._dict(href=sysd.base_url, external=1, system=sysd.name, none=not sysd.base_url)
    item.action = action


def logo():
    s = site()
    if s.get("logo"):
        return s.logo
    try:
        ws = _ws()
        return ws.get("banner_image") or ws.get("app_logo") or "/assets/pcpb_website/images/pcpb-logo.svg"
    except Exception:
        return "/assets/pcpb_website/images/pcpb-logo.svg"


def lines(text):
    return _lines(text)


def md(text):
    """Rich text stored by the builder is HTML; text typed as Markdown in the Desk is converted."""
    text = text or ""
    if "<" in text and ">" in text:
        return frappe.utils.sanitize_html(text) if not text.strip().startswith("<!--raw-->") else text
    return frappe.utils.md_to_html(text) or ""


def _safe(impl, default, name=None):
    def wrapper(*a, **k):
        try:
            return impl(*a, **k)
        except Exception:
            frappe.log_error(title=f"PCPB Website: {impl.__name__} failed")
            return default
    # Jinja finds these by name, so the name is the one used in templates
    wrapper.__name__ = name or impl.__name__.strip("_").replace("_impl", "")
    return wrapper


def _services_any():
    """Services from this server, or from the ERP when the website is hosted apart from it."""
    from pcpb_website import remote
    if not remote.on():
        return _services_impl()
    base, out = _portal_base(), []
    for row in remote.fetch("public_services", default=[]) or []:
        item = frappe._dict(row)
        action = frappe._dict(item.get("action") or {"none": True})
        if action.get("href") and str(action.href).startswith("/"):
            # a portal address: the portal lives with the ERP (or at the Portal Address in Settings)
            action.href = (base or remote.erp_base()) + action.href
        item.action = action
        out.append(item)
    return out


def _featured_any(limit=6):
    svc = _services_any()
    flagged = [x for x in svc if x.featured]
    return (flagged or svc)[: int(limit or 6)]


def _vacancies_any(limit=50):
    """Vacancies from HR on this server, or from the ERP. The job page and the application form stay with HR."""
    from pcpb_website import remote
    if not remote.on():
        return _vacancies_impl(limit)
    out = []
    for row in remote.fetch("public_vacancies", dict(limit=limit), default=[]) or []:
        v = frappe._dict(row)
        if v.get("url") and str(v.url).startswith("/"):
            v.url = remote.erp_base() + v.url
        out.append(v)
    return out


leaders = _safe(_leaders_impl, [])
vacancies = _safe(_vacancies_any, [], "vacancies")
featured_services = _safe(_featured_any, [], "featured_services")
posts = _safe(_posts_impl, [])
documents = _safe(_documents_impl, [])
services = _safe(_services_any, [], "services")
tenders = _safe(_tenders_impl, [])
ticker = _safe(_ticker_impl, [])
offices = _safe(_offices_impl, [])
