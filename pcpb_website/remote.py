"""The link between a website server and an ERP server that are hosted apart.

The same app is installed on both. Desk > PCPB Website > Integration Settings holds the Deployment Mode:

  * Single server (website and ERP together)   everything is read from this site's own database (the default)
  * Website server (ERP hosted separately)     registers, services and vacancies are fetched from the ERP's API
  * ERP server (website hosted separately)     this site answers those requests and shows no public website

Authentication is the standard Frappe one: an API key and secret of an ERP user (User > Settings > API Access),
sent as "Authorization: token <key>:<secret>". That user holds the role PCPB Website Integration and nothing else.
Only data that is already public is exchanged: the same register fields and the same filters a visitor sees.
"""
import functools
import hashlib
import json

import frappe
from frappe.rate_limiter import rate_limit

from pcpb_website.pcpb_website.doctype.pcpb_website_integration.pcpb_website_integration import ERP, INTEGRATION_ROLE, SINGLE, WEBSITE


def settings():
    return frappe.get_cached_doc("PCPB Website Integration")


def mode():
    return settings().get("deployment_mode") or SINGLE


def on():
    """True on a website server whose ERP is hosted separately."""
    s = settings()
    return s.get("deployment_mode") == WEBSITE and bool(s.get("erp_url"))


def is_provider():
    """True on an ERP server whose website is hosted separately."""
    return settings().get("deployment_mode") == ERP


def erp_base():
    return (settings().get("erp_url") or "").rstrip("/")


def _headers():
    s = settings()
    headers = {"Accept": "application/json"}
    secret = s.get_password("api_secret", raise_exception=False) if s.get("api_key") else None
    if s.get("api_key") and secret:
        headers["Authorization"] = f"token {s.api_key}:{secret}"
    return headers


def trusted_caller():
    """The website server signs in with its API key. Frappe has already checked the key by the time this runs."""
    user = frappe.session.user
    return bool(user and user != "Guest" and INTEGRATION_ROLE in frappe.get_roles(user))


def public(limit, seconds=60):
    """Guest endpoint with a per-visitor request limit. The signed-in website server is not limited."""
    def deco(fn):
        limited = rate_limit(limit=limit, seconds=seconds)(fn)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs) if trusted_caller() else limited(*args, **kwargs)
        return wrapper
    return deco


def fetch(method, params=None, ttl=None, default=None):
    """Call the ERP API. Answers are cached for `ttl` seconds; if the ERP cannot be reached the last good answer
    is returned, so a short ERP outage does not empty the website."""
    import requests

    params = {k: v for k, v in (params or {}).items() if v not in (None, "")}
    s = settings()
    ttl = int(s.get("cache_seconds") or 0) if ttl is None else ttl
    digest = hashlib.sha1(json.dumps([erp_base(), method, params], sort_keys=True, default=str).encode()).hexdigest()
    fresh, stale = f"pcpb_remote:{digest}", f"pcpb_remote_last:{digest}"
    if ttl:
        hit = frappe.cache.get_value(fresh)
        if hit is not None:
            return hit
    try:
        r = requests.get(f"{erp_base()}/api/method/pcpb_website.api.{method}", params=params, headers=_headers(),
                         timeout=int(s.get("request_timeout") or 10))
        if r.status_code == 404:
            raise frappe.DoesNotExistError
        r.raise_for_status()
        data = r.json().get("message")
    except frappe.DoesNotExistError:
        raise
    except Exception:
        last = frappe.cache.get_value(stale)
        if last is not None:
            return last
        frappe.log_error(title=f"PCPB Website: the ERP API did not answer ({method})")
        return default
    if ttl:
        frappe.cache.set_value(fresh, data, expires_in_sec=ttl)
    frappe.cache.set_value(stale, data, expires_in_sec=24 * 3600)
    return data


@frappe.whitelist()
def test_connection():
    """Test Connection button in Integration Settings. The result is also recorded on the form."""
    frappe.only_for(["System Manager", "Website Manager"])
    import requests

    s = settings()
    if s.get("deployment_mode") != WEBSITE:
        return {"ok": True, "message": f"Deployment Mode is '{mode()}'. This site does not call another server."}
    base = erp_base()
    ok, info = False, {}
    if not base:
        message = "Enter the ERP Address first."
    else:
        try:
            r = requests.get(f"{base}/api/method/pcpb_website.api.link_status", headers=_headers(), timeout=int(s.get("request_timeout") or 10))
            if r.status_code in (401, 403):
                message = "The ERP rejected the API Key or Secret. Issue new keys for the integration user on the ERP and enter them here."
            else:
                r.raise_for_status()
                info = r.json().get("message") or {}
                ok = True
                auth = "Signed in with the API key." if info.get("trusted") else \
                    "Not signed in: no API key is set, or its user lacks the PCPB Website Integration role, so requests are limited like a visitor's."
                message = (f"Connected to {info.get('site_name') or base}. Registers published: {info.get('registers', 0)}. "
                           f"Services: {info.get('services', 0)}. Open vacancies: {info.get('vacancies', 0)}. {auth}")
        except Exception as e:
            message = (f"Could not reach the ERP at {base}. Check the address, that the PCPB Website app is installed there, "
                       f"and that this server may reach it over HTTPS. ({type(e).__name__})")
    frappe.db.set_single_value("PCPB Website Integration", {"connection_status": ("" if ok else "Failed. ") + message[:130],
                                                            "last_checked": frappe.utils.now_datetime()}, update_modified=False)
    frappe.db.commit()
    return {"ok": ok, "message": message, "info": info}


# ---------------------------------------------------------------- portals
def portal(audience="Customers and applicants"):
    """The enabled portal for an audience, with its address worked out. None when there is no such portal."""
    for p in settings().get("portals") or []:
        if p.enabled and p.audience == audience:
            base = (p.base_url or "").rstrip("/") or (erp_base() if on() else "")
            return frappe._dict(name=p.portal_name, audience=p.audience, base=base, show_in_header=int(p.show_in_header or 0),
                                sign_in=base + (p.sign_in_path or "/login"), sign_up=base + (p.sign_up_path or "/signup"),
                                home=base + (p.home_path or "/portal"), verify=(base + p.verify_path) if p.verify_path else "")
    return None
