import frappe

no_header = 1
show_sidebar = False
no_cache = 1

from pcpb_website.utils import tr


def get_context(context):
    name = (frappe.form_dict.get("name") or "").strip()
    if not name or not frappe.db.exists("PCPB Tender", {"name": name, "published": 1}):
        raise frappe.DoesNotExistError
    doc = frappe.get_doc("PCPB Tender", name)
    context.tender = frappe._dict(
        name=doc.name, tender_no=doc.tender_no, category=doc.category, status=doc.effective_status,
        status_label=tr("tender_" + doc.effective_status.lower()),
        title=doc.title,
        summary=doc.summary or "",
        body=doc.description or "",
        published_on=doc.published_on, closing_on=doc.closing_on,
        submission=doc.submission_note, contact=doc.contact_email, award=doc.award_note,
        documents=[frappe._dict(type=d.doc_type, label=d.label, file=d.file) for d in doc.documents if d.file])
    context.title = context.tender.title
    context.pcpb_own = 1
    context.pcpb_edit_link = f"/desk/pcpb-tender/{doc.name}"
