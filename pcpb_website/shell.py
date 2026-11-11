"""Decides which website pages wear the PCPB header and footer."""
import frappe

BASE = "templates/pcpb_base.html"


def _excluded(path, s):
    path = (path or "").strip("/").lower()
    for line in (s.get("shell_exclude") or "").splitlines():
        p = line.strip().strip("/").lower()
        if not p:
            continue
        if p.endswith("*"):
            if path.startswith(p[:-1]):
                return True
        elif path == p or path.startswith(p + "/"):
            return True
    return False


def update_website_context(context):
    try:
        from pcpb_website import remote
        from pcpb_website.utils import site
        s = site()
        if remote.is_provider() and not context.get("pcpb_own"):
            return context  # this server only supplies data; it shows no public website of its own
        path = context.get("path") or getattr(frappe.local, "path", "") or ""
        own = bool(context.get("pcpb_own"))
        if own or (int(s.get("shell_everywhere") or 0) and not _excluded(path, s)):
            context.base_template_path = BASE
            context.body_class = ((context.get("body_class") or "") + " pc-site" + (" pc-own" if own else " pc-foreign")).strip()
    except Exception:
        frappe.log_error(title="PCPB Website: shell could not be applied")
    return context


def home_page(user=None):
    """Home page for everyone = Website Settings > Home Page (set from the builder). Empty lets Frappe decide."""
    try:
        from pcpb_website import remote
        if remote.is_provider():
            return None
        return (frappe.db.get_single_value("Website Settings", "home_page") or "").strip("/") or None
    except Exception:
        return None
