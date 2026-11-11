"""Turns the sections of a page into HTML.

A page is a standard Web Page whose content type is Page Builder. Each section is a standard Web Template plus
the values the editor typed.
"""
import json

import frappe



def _json(v):
    if isinstance(v, (dict, list)):
        return v
    try:
        return json.loads(v) if v else {}
    except Exception:
        return {}


def live_blocks(doc):
    """Sections of the published page, in the neutral shape the builder and renderer share."""
    out = []
    for b in doc.get("page_blocks") or []:
        out.append({
            "web_template": b.web_template, "values": _json(b.web_template_values),
            "hide": int(b.hide_block or 0), "shade": int(b.add_shade or 0), "section_id": b.section_id or "",
            "css_class": b.css_class or "",
        })
    return out


def draft_of(doc):
    d = _json(doc.get("pcpb_draft"))
    return d if isinstance(d, dict) and isinstance(d.get("blocks"), list) else None


def render_block(block, edit=False, idx=0):
    name = block.get("web_template")
    hidden = int(block.get("hide") or 0)
    if hidden and not edit:
        return ""
    try:
        tpl = frappe.get_cached_doc("Web Template", name)
        vals = dict(block.get("values") or {})
        vals["pb_edit"] = 1 if edit else 0
        vals["pb_idx"] = idx
        inner = tpl.render(vals)
        if not name.startswith("PCPB "):
            inner = f'<div class="pc-wrap pc-pad pc-stock">{inner}</div>'
    except Exception:
        frappe.log_error(title=f"PCPB Website: section {name} failed")
        if not edit:
            return ""
        inner = ('<div class="pc-wrap pc-pad"><div class="pc-note pc-bad">This section could not be shown. '
                 'Open it and check its settings, or remove it.</div></div>')
    cls = ["pc-sec"]
    if int(block.get("shade") or 0):
        cls.append("pc-alt")
    if hidden:
        cls.append("pb-hidden")
    if block.get("css_class"):
        cls.append(frappe.utils.escape_html(block["css_class"]))
    sid = frappe.utils.escape_html(block.get("section_id") or "")
    return (f'<section class="{" ".join(cls)}"{f" id=\"{sid}\"" if sid else ""} data-pb="{idx}" '
            f'data-pb-template="{frappe.utils.escape_html(name or "")}">{inner}</section>')


def render_blocks(blocks, edit=False):
    return "".join(render_block(b, edit, i) for i, b in enumerate(blocks or []))


def apply_draft(doc):
    """Copy the saved draft onto the live page. Called when the page reaches a published state."""
    d = draft_of(doc)
    if not d:
        return False
    if d.get("title"):
        doc.title = d["title"]
    doc.meta_description = d.get("meta_description") or ""
    doc.content_type = "Page Builder"
    doc.set("page_blocks", [])
    for b in d["blocks"]:
        if not b.get("web_template") or not frappe.db.exists("Web Template", b["web_template"]):
            continue
        doc.append("page_blocks", {
            "web_template": b["web_template"], "web_template_values": json.dumps(b.get("values") or {}),
            "hide_block": int(b.get("hide") or 0),
            "add_shade": int(b.get("shade") or 0), "section_id": b.get("section_id") or "", "css_class": b.get("css_class") or "",
            "add_container": 0, "add_top_padding": 0, "add_bottom_padding": 0,
        })
    doc.pcpb_draft = ""
    return True


def page_context(doc, context, edit=False, use_draft=False):
    """Everything the page template needs, for a live visit or for the builder."""
    draft = draft_of(doc) if (edit or use_draft) else None
    blocks = draft["blocks"] if draft else live_blocks(doc)
    title = (draft or {}).get("title") or doc.title
    context.title = title
    context.pcpb_page = doc.name
    context.pcpb_blocks_html = render_blocks(blocks, edit)
    context.pcpb_is_builder_page = doc.content_type == "Page Builder" or bool(draft)
    context.pcpb_edit = 1 if edit else 0
    context.no_cache = 1
    context.no_breadcrumbs = 1
    context.no_header = 1
    context.show_sidebar = False
    return context
