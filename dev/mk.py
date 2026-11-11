"""Dev helper: compact DocType JSON writer."""
import json, os, re
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pcpb_website", "pcpb_website", "doctype")
EDIT_ROLES = ["System Manager", "Website Manager", "Website Content Editor", "Website Content Approver", "Website Publisher"]

def scrub(n): return n.lower().replace(" ", "_")

def F(spec, **kw):
    """'fieldname:Type[:options]' ; label derived unless given."""
    p = spec.split(":", 2)
    fn, ft = p[0], p[1]
    d = {"fieldname": fn, "fieldtype": ft}
    if ft not in ("Column Break",):
        d["label"] = kw.pop("label", None) or fn.replace("_", " ").title()
    if len(p) > 2: d["options"] = p[2].replace("|", "\n")
    d.update(kw)
    return d

def doctype(name, fields, single=False, child=False, autoname=None, title_field=None, roles=None, naming_rule=None, **extra):
    d = {"doctype": "DocType", "name": name, "module": "PCPB Website", "custom": 0, "engine": "InnoDB",
         "fields": fields, "field_order": [f["fieldname"] for f in fields],
         "creation": "2026-11-11 10:00:00", "modified": extra.pop("modified", "2026-11-11 10:00:00"), "modified_by": "Administrator", "owner": "Administrator",
         "sort_field": "modified", "sort_order": "DESC", "permissions": []}
    if single: d["issingle"] = 1
    if child: d["istable"] = 1; d["editable_grid"] = 1
    if autoname: d["autoname"] = autoname
    if naming_rule: d["naming_rule"] = naming_rule
    if title_field: d["title_field"] = title_field; d["show_title_field_in_link"] = 1
    if not child:
        for r in (roles or EDIT_ROLES):
            p = {"role": r, "read": 1, "write": 1, "create": 1, "delete": 1 if r in ("System Manager", "Website Manager") else 0, "email": 1, "print": 1, "report": 1, "export": 1, "share": 1}
            if single: p.pop("report"); p.pop("export")
            d["permissions"].append(p)
    d.update(extra)
    folder = os.path.join(ROOT, scrub(name)); os.makedirs(folder, exist_ok=True)
    json.dump(d, open(os.path.join(folder, scrub(name) + ".json"), "w"), indent=1)
    open(os.path.join(folder, "__init__.py"), "a").close()
    py = os.path.join(folder, scrub(name) + ".py")
    if not os.path.exists(py):
        cls = name.replace(" ", "")
        open(py, "w").write(f"from frappe.model.document import Document\n\n\nclass {cls}(Document):\n    pass\n")
    return d
