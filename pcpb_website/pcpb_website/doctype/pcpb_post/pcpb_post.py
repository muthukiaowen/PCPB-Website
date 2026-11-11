import re

import frappe
from frappe.website.website_generator import WebsiteGenerator


class PCPBPost(WebsiteGenerator):
    website = frappe._dict(
        condition_field="published",
        page_title_field="title",
        template="templates/generators/pcpb_post.html",
    )

    def validate(self):
        route = (self.route or "").strip().strip("/").lower()
        if not route:
            slug = re.sub(r"[^a-z0-9]+", "-", (self.title or "").lower()).strip("-")[:80]
            route = f"news/{slug}"
        self.route = route
        if not self.publish_date:
            self.publish_date = frappe.utils.nowdate()

    def get_context(self, context):
        from pcpb_website.utils import tr_value
        context.title = self.title
        context.page_title = context.title
        context.body = self.body
        context.summary = self.summary
        context.type_label = tr_value(self.post_type)
        context.metatags = {"title": context.title, "description": self.meta_description or context.summary,
                            "image": self.hero_image}
        context.pcpb_own = 1
        context.pcpb_edit_link = f"/desk/pcpb-post/{self.name}"
        context.no_cache = 1
        context.no_breadcrumbs = 1
        return context
