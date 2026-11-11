from mk import F, doctype

# ---------------- settings (single)
doctype("PCPB Website Settings", [
    F("tab_identity:Tab Break", label="Identity"),
    F("site_name:Data", label="Organisation Name", reqd=1),
    F("tagline:Data"),
    F("parent_body:Data", label="Parent Ministry or Department", description="Shown in small print under the name in the header"),
    F("cb_id:Column Break"),
    F("logo:Attach Image", label="Logo", description="Shown in the header on every page. A square or wide PNG or SVG with a transparent background works best."),
    F("logo_alt:Data", label="Logo Description", description="Read out by screen readers, for example: Pest Control Products Board logo"),
    F("logo_on_desk:Check", label="Use this logo in the Desk as well", default="1", description="The PCPB Website icon on the Desk home screen, and the logo at the top of the Desk and on the sign-in page, follow the logo above. A Desk logo that somebody chose separately in Navbar Settings is left alone."),
    F("desk_logo_set:Data", label="Desk Logo Set By Website", hidden=1, read_only=1),
    F("footer_logo:Attach Image", label="Footer Logo (optional)", description="A light version for the dark footer. Leave empty to show the name only."),
    F("identity_help:HTML", label="Identity Help", options="<p class='text-muted'>The browser tab icon is set in <a href='/desk/website-settings'>Website Settings &gt; Favicon</a>, or from the website builder under Logo and name.</p>"),

    F("tab_theme:Tab Break", label="Theme"),
    F("color_primary:Color", label="Main Colour"), F("color_dark:Color", label="Dark Colour (headers, footer)"),
    F("color_accent:Color", label="Accent Colour (buttons, highlights)"), F("color_soft:Color", label="Soft Tint (panels)"),
    F("cb_theme:Column Break"),
    F("color_bg:Color", label="Page Background"), F("color_text:Color", label="Text Colour"),
    F("font_body:Select:Inter|System|Arial|Georgia|Verdana", label="Body Font", default="Inter"),
    F("font_heading:Select:Serif|Same as body|Georgia", label="Heading Font", default="Serif"),
    F("sb_theme2:Section Break", label="Shape and layout"),
    F("radius:Int", label="Corner Roundness (px)", default="14"),
    F("page_width:Int", label="Page Width (px)", default="1220"),
    F("cb_theme2:Column Break"),
    F("show_flag_bar:Check", label="Show the national colours strip", default="1"),
    F("allow_dark_mode:Check", label="Offer a dark mode button", default="1"),
    F("allow_text_size:Check", label="Offer text size buttons", default="1"),
    F("sb_theme3:Section Break", label="Extra CSS (ICT only)", collapsible=1),
    F("custom_css:Code:CSS", label="Extra CSS"),

    F("tab_header:Tab Break", label="Header"),
    F("gov_bar:Data", label="Top Strip Text", default="Republic of Kenya"),
    F("show_search:Check", label="Show the search box in the header", default="1"),
    F("show_portal_links:Check", label="Show Sign in and Create account", default="1"),
    F("sb_translate:Section Break", label="Translation"),
    F("show_translate:Check", label="Show the Translate button", default="1", description="Visitors choose a language and Google Translate translates the page for them. The English text stays the official version."),
    F("translate_languages:Small Text", label="Languages Offered", description="One per line, as code:Name. Codes are Google Translate language codes.", default="sw:Kiswahili\nfr:French\nar:Arabic\nso:Somali"),
    F("sb_ticker:Section Break", label="Notices ticker"),
    F("show_ticker:Check", label="Show the notices ticker", default="1"),
    F("ticker_posts:Int", label="Include this many latest posts marked for the ticker", default="5"),
    F("ticker_items:Table:PCPB Ticker Item", label="Fixed ticker items"),

    F("tab_contact:Tab Break", label="Contact"),
    F("address:Small Text"), F("phone:Data"), F("email:Data"), F("hours:Data", label="Opening Hours"),
    F("cb_contact:Column Break"),
    F("map_lat:Data", label="Map Latitude"), F("map_lng:Data", label="Map Longitude"), F("map_zoom:Int", label="Map Zoom", default="15"),
    F("social_x:Data", label="X (Twitter) Link"), F("social_facebook:Data", label="Facebook Link"),
    F("social_linkedin:Data", label="LinkedIn Link"), F("social_youtube:Data", label="YouTube Link"),
    F("sb_offices:Section Break", label="Offices"),
    F("offices:Table:PCPB Office", label="Offices"),

    F("tab_footer:Tab Break", label="Footer"),
    F("footer:Small Text", label="About Text"),
    F("footer_note:Data", label="Bottom Note"),
    F("footer_help:HTML", label="Footer Help", options="<p class='text-muted'>Footer link columns come from <a href='/desk/website-settings'>Website Settings &gt; Footer</a>. Items with the same Parent Label form one column.</p>"),

    F("tab_shell:Tab Break", label="Where the design applies"),
    F("shell_everywhere:Check", label="Use the PCPB header and footer on other website pages too (job pages, web forms)", default="1"),
    F("shell_exclude:Small Text", label="Never apply on addresses starting with", description="One per line. The applicant portal and sign-in pages keep their own design. End a line with * to match everything that starts with it, for example my-*",
      default="portal\nlogin\nsignup\napply\nverify\nservices\nhome\nmy-*\nme\nupdate-password\napp\ndesk\nprintview\napi"),

    F("tab_words:Tab Break", label="Wording"),
    F("ui_labels:Table:PCPB UI Label", label="Interface Wording", description="Every fixed word or phrase on the site (button names, messages). Change the wording here; do not change the key."),
    F("defaults_loaded:Check", hidden=1), F("builder_seeded:Check", hidden=1), F("defaults_applied:Small Text", hidden=1), F("help_seeded:Small Text", hidden=1),
], single=True, roles=["System Manager", "Website Manager"], modified="2026-11-15 09:00:00")

doctype("PCPB Ticker Item", [
    F("tag:Data", label="Tag", in_list_view=1, columns=2),
    F("text:Data", label="Text", in_list_view=1, reqd=1, columns=5),
    F("url:Data", label="Link", in_list_view=1, columns=3),
], child=True, modified="2026-11-12 09:00:00")

doctype("PCPB UI Label", [
    F("key:Data", label="Key", in_list_view=1, reqd=1, read_only=0, columns=3),
    F("wording:Small Text", label="Wording", in_list_view=1, columns=7),
], child=True, modified="2026-11-12 09:00:00")

doctype("PCPB Office", [
    F("office_name:Data", in_list_view=1, reqd=1, columns=3), F("address:Small Text", in_list_view=1, columns=3),
    F("phone:Data", in_list_view=1, columns=2), F("email:Data", in_list_view=1, columns=2),
    F("lat:Data", label="Latitude"), F("lng:Data", label="Longitude"),
], child=True)

# ---------------- registers
doctype("PCPB Register Group", [
    F("group_name:Data", label="Group Name", reqd=1, unique=1, in_list_view=1),
    F("description:Small Text", in_list_view=1),
    F("display_order:Int", default="10", in_list_view=1),
], autoname="field:group_name", naming_rule="By fieldname", roles=["System Manager", "Website Manager"], modified="2026-11-12 09:00:00")

doctype("PCPB Register Field", [
    F("fieldname:Data", label="Field", reqd=1, in_list_view=1, columns=2, description="A field of the source record, or table.column for a column of one of its tables"),
    F("public:Check", label="Public", in_list_view=1, columns=1, default="1"),
    F("label:Data", label="Label", in_list_view=1, columns=3),
    F("in_list:Check", label="In the table", in_list_view=1, columns=1, default="1"),
    F("in_detail:Check", label="On the record page", in_list_view=1, columns=1, default="1"),
    F("searchable:Check", label="Searchable", in_list_view=1, columns=1),
    F("filterable:Check", label="Dropdown filter", in_list_view=1, columns=1),
], child=True, modified="2026-11-12 09:00:00")

doctype("PCPB Register", [
    F("title:Data", reqd=1, in_list_view=1),
    F("slug:Data", label="Address", reqd=1, unique=1, description="Lower case, no spaces. The register opens at /registers/<address>"),
    F("route:Data", label="Own Address (optional)", unique=1, description="Gives the register an address of its own, for example memos opens it at /memos and each record at /memos/<record>. Leave empty to use /registers/<address>."),
    F("register_group:Link:PCPB Register Group", in_list_view=1, in_standard_filter=1),
    F("cb1:Column Break"),
    F("published:Check", in_list_view=1), F("display_order:Int", default="10"),
    F("icon:Select:leaf|sprout|shield|flask|alert|clock|grid|limit|ban|doc|building|search|users|briefcase", default="leaf"),
    F("status_kind:Select:Standard|Restricted|Withdrawn|Banned|Documents", label="Kind", default="Standard", description="Restricted, Withdrawn and Banned registers are used by the product status check to warn the public"),
    F("sb_text:Section Break", label="Description"),
    F("description:Small Text"),
    F("sb_src:Section Break", label="Where the data comes from"),
    F("source_doctype:Link:DocType", label="Records Of", reqd=1, description="The ERP record type this register reads live, e.g. Product or Premises"),
    F("public_filter:Code:JSON", label="Which Records Are Public", description="Nothing is shown until this is set. Example: {\"status\": \"Registered\"}. Use \"__today__\" for today's date, e.g. {\"valid_to\": [\">=\", \"__today__\"]}"),
    F("add_publish_tick:Button", label="Add a Publish on Website tick to this record type", description="Adds a standard Custom Field (a tick box named Publish on Website) to the record type and makes it the rule above. Staff then publish a record to the website by ticking it on the ERP record."),
    F("cb_src:Column Break"),
    F("title_field:Data", label="Record Title Field", description="The field shown as the heading of a record page"),
    F("ingredient_field:Data", label="Active Ingredient Field", description="Used by the product status check to match restricted, withdrawn and banned lists"),
    F("sort_field:Data", label="Sort By Field"), F("sort_dir:Select:asc|desc", label="Sort Direction", default="asc"),
    F("page_length:Int", label="Rows Per Page", default="25"),
    F("allow_export:Check", label="Allow the public to download the list (CSV)", default="1"),
    F("sb_fields:Section Break", label="Fields shown to the public"),
    F("load_fields:Button", label="List all fields of the record type"),
    F("fields:Table:PCPB Register Field", label="Fields"),
], autoname="field:slug", naming_rule="By fieldname", title_field="title", roles=["System Manager", "Website Manager"], modified="2026-11-15 09:00:00")

# ---------------- posts (news, notices)
doctype("PCPB Post", [
    F("title:Data", reqd=1, in_list_view=1),
    F("route:Data", label="Address", description="Filled in for you from the title. Example: news/new-fee-schedule"),
    F("post_type:Select:News|Notice|Circular|Safety Alert|Announcement|Press Release|Event", label="Type", default="News", in_list_view=1, in_standard_filter=1),
    F("cb0:Column Break"),
    F("published:Check", in_list_view=1), F("publish_date:Date", default="Today", in_list_view=1),
    F("expires_on:Date", label="Move To Archive After"),
    F("show_in_ticker:Check", label="Show in the notices ticker"),
    F("sb1:Section Break", label="Content"), F("summary:Small Text", description="One or two sentences shown in lists and under the title"), F("body:Text Editor"),
    F("sb3:Section Break", label="Picture and files"), F("hero_image:Attach Image", label="Picture"), F("hero_alt:Data", label="Picture Description"),
    F("files:Table:PCPB Page File", label="Files"),
    F("sb4:Section Break", label="Search engines", collapsible=1), F("meta_description:Small Text", label="Description For Search Engines"),
], autoname="format:POST-{#####}", title_field="title", has_web_view=1, allow_guest_to_view=1, is_published_field="published", index_web_pages_for_search=1, modified="2026-11-12 09:00:00")

# ---------------------------------------------------------------- integration (hosting, ERP API, portals)
DEPLOY = "Single server (website and ERP together)|Website server (ERP hosted separately)|ERP server (website hosted separately)"
WEB = "eval:doc.deployment_mode=='Website server (ERP hosted separately)'"
ERP = "eval:doc.deployment_mode=='ERP server (website hosted separately)'"
doctype("PCPB Website Integration", [
    F("sb_deploy:Section Break", label="Deployment"),
    F("deployment_mode:Select:" + DEPLOY, label="Deployment Mode", reqd=1, default="Single server (website and ERP together)",
      description="How the public website and the ERP are hosted. The PCPB Website app is installed on each server and this setting says which part that server plays."),
    F("cb_deploy:Column Break"),
    F("deploy_help:HTML", label="Deployment Help", options="<p class='text-muted'><b>Single server</b>: one site runs the website and the ERP; nothing else to set.<br><b>Website server</b>: this site shows the public website and reads registers, services and vacancies from the ERP through its API.<br><b>ERP server</b>: this site holds the records and answers the website's API requests; it shows no public website.</p>"),

    F("sb_api:Section Break", label="ERP API connection", depends_on=WEB),
    F("erp_url:Data", label="ERP Address", options="URL", mandatory_depends_on=WEB, description="Base address of the ERP site, for example https://erp.pcpb.go.ke"),
    F("api_key:Data", label="API Key", description="From the integration user on the ERP: User > Settings > API Access"),
    F("api_secret:Password", label="API Secret"),
    F("cb_api:Column Break"),
    F("cache_seconds:Int", label="Cache Duration (seconds)", default="120", description="How long an ERP answer is reused before the ERP is asked again. 0 turns caching off."),
    F("request_timeout:Int", label="Request Timeout (seconds)", default="10"),
    F("test_connection:Button", label="Test Connection"),
    F("connection_status:Data", label="Last Connection Result", read_only=1),
    F("last_checked:Datetime", label="Last Checked", read_only=1),

    F("sb_provider:Section Break", label="API access for the website", depends_on=ERP),
    F("provider_help:HTML", label="API Access Help", options="<p class='text-muted'>The website server signs in to this ERP with a standard API key. Create the integration user here, then copy its API Key and API Secret into Integration Settings on the website server. The user has one role, <b>PCPB Website Integration</b>, which gives it nothing beyond the public register, service and vacancy data.</p>"),
    F("integration_user:Link:User", label="Integration User", read_only=1),
    F("create_api_user:Button", label="Create Integration User and API Keys"),

    F("sb_portals:Section Break", label="Portals"),
    F("portal_help:HTML", label="Portals Help", options="<p class='text-muted'>Each portal the public is sent to. Leave the address empty when a portal is on the ERP site (or on this site when everything is on one server). Sign in, Create an account and Apply use the portal whose audience is <b>Customers and applicants</b>. Tender pages offer the <b>Suppliers</b> portal.</p>"),
    F("portals:Table:PCPB Portal", label="Portals"),
], single=True, roles=["System Manager", "Website Manager"], modified="2026-11-14 09:00:00")

doctype("PCPB Portal", [
    F("portal_name:Data", label="Portal Name", reqd=1, in_list_view=1, columns=2),
    F("audience:Select:Customers and applicants|Suppliers|Other", label="Audience", reqd=1, default="Customers and applicants", in_list_view=1, columns=2),
    F("enabled:Check", label="Enabled", default="1", in_list_view=1, columns=1),
    F("base_url:Data", label="Address", options="URL", in_list_view=1, columns=3, description="Empty = hosted with the ERP. Otherwise the full address, for example https://portal.pcpb.go.ke"),
    F("show_in_header:Check", label="Show in Website Header", default="1", in_list_view=1, columns=1),
    F("sb_paths:Section Break", label="Pages on the portal"),
    F("sign_in_path:Data", label="Sign-in Page", default="/login"),
    F("sign_up_path:Data", label="Registration Page", default="/signup"),
    F("cb_paths:Column Break"),
    F("home_path:Data", label="Portal Home Page", default="/portal"),
    F("verify_path:Data", label="Certificate Verification Page", description="Customer portal only, for example /verify"),
], child=True, modified="2026-11-14 09:00:00")
