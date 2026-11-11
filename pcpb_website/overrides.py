import frappe
from frappe.website.doctype.web_page.web_page import WebPage

from pcpb_website.render import apply_draft, page_context


def _provider():
    from pcpb_website import remote
    return remote.is_provider()


class PCPBWebPage(WebPage):
    """Standard Web Page, shown inside the PCPB design, with a draft that goes live on publish."""

    def validate(self):
        super().validate()
        self._publish_draft_if_due()

    def _publish_draft_if_due(self):
        """When the approval workflow moves the page into a published state, the saved draft becomes the live page."""
        if not self.get("pcpb_draft") or not self.meta.has_field("workflow_state"):
            return
        if self.is_new() or not self.has_value_changed("workflow_state"):
            return
        from frappe.model.workflow import get_workflow_name
        wf = get_workflow_name("Web Page")
        if not wf:
            return
        for st in frappe.get_cached_doc("Workflow", wf).states:
            if st.state == self.workflow_state and st.update_field == "published" and str(st.update_value) == "1":
                apply_draft(self)
                return

    def set_page_blocks(self, context):
        # Sections are rendered by pcpb_website.render so that the PCPB design applies.
        if _provider():
            return super().set_page_blocks(context)
        return

    def get_context(self, context):
        super().get_context(context)
        if _provider():
            return context  # an ERP-only server keeps Frappe's own page rendering
        from pcpb_website.utils import can_edit
        preview = bool(frappe.form_dict.get("draft")) and can_edit()
        page_context(self, context, edit=False, use_draft=preview)
        context.template = "templates/pcpb_web_page.html"
        context.pcpb_own = 1
        context.pcpb_edit_link = f"/page-builder?page={frappe.utils.quote(self.name)}"
        return context
