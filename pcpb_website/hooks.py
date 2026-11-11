app_name = "pcpb_website"
app_title = "PCPB Website"
app_publisher = "Titansoft"
app_description = "PCPB public website on the Frappe Website module, with a visual page builder"
app_email = "info@titansoft.africa"
app_license = "mit"

# Pages are standard Web Pages. This class shows them inside the PCPB design and adds drafts.
override_doctype_class = {"Web Page": "pcpb_website.overrides.PCPBWebPage"}

# Record pages. Lists (registers, tenders, news, careers ...) are ordinary pages built from sections.
website_route_rules = [
    {"from_route": "/registers/<register>", "to_route": "register-list"},
    {"from_route": "/registers/<register>/<name>", "to_route": "register-record"},
    {"from_route": "/online-services/<slug>", "to_route": "service-detail"},
    {"from_route": "/tenders/<name>", "to_route": "tender-detail"},
]

# Registers with an address of their own (for example /memos).
page_renderer = ["pcpb_website.routes.RegisterPage"]

# The PCPB header and footer wrap website pages (see PCPB Website Settings > Where the design applies).
update_website_context = ["pcpb_website.shell.update_website_context"]

# The home page is whatever Website Settings > Home Page says, so staff can change it from the builder.
get_website_user_home_page = "pcpb_website.shell.home_page"

jinja = {"methods": [
    "pcpb_website.utils.tr",
    "pcpb_website.utils.tr_value",
    "pcpb_website.utils.lurl",
    "pcpb_website.utils.translate_languages",
    "pcpb_website.utils.menu_tree",
    "pcpb_website.utils.footer_columns",
    "pcpb_website.utils.inline_css",
    "pcpb_website.utils.asset_version",
    "pcpb_website.utils.can_edit",
    "pcpb_website.utils.leaders",
    "pcpb_website.utils.vacancies",
    "pcpb_website.utils.featured_services",
    "pcpb_website.utils.site",
    "pcpb_website.utils.services",
    "pcpb_website.utils.logo",
    "pcpb_website.utils.posts",
    "pcpb_website.utils.documents",
    "pcpb_website.utils.tenders",
    "pcpb_website.utils.ticker",
    "pcpb_website.utils.offices",
    "pcpb_website.utils.lines",
    "pcpb_website.utils.md",
    "pcpb_website.utils.apply_url",
    "pcpb_website.utils.portal_link",
    "pcpb_website.utils.portals",
    "pcpb_website.api.registers",
    "pcpb_website.api.register_groups",
    "pcpb_website.api.register_count",
    "pcpb_website.icons.icon",
]}

before_install = "pcpb_website.install.ensure_roles"
after_install = "pcpb_website.install.after_install"
after_migrate = ["pcpb_website.install.after_migrate"]

add_to_apps_screen = [{
    "name": "pcpb_website",
    "logo": "/api/method/pcpb_website.api.app_logo",  # forwards to the uploaded logo
    "title": "PCPB Website",
    "route": "/desk/pcpb-website",
}]
