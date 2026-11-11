"""Dev helper: writes the native Module Onboarding and its Onboarding Steps (the Getting started guide).
After install these are ordinary records: edit them in Desk > Onboarding Step. Run:  python3 dev/onboarding.py"""
import json, os, shutil

MOD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pcpb_website", "pcpb_website")
NAME = "PCPB Website Onboarding"
GUIDE = "/website-guide"
# name, title, action, action_label, target (path or doctype), optional, description
STEPS = [
    ("PCPB Website Identity", "Upload the logo and set the organisation name", "Go to Page", "Open Logo and Name", "/page-builder?panel=identity", 0,
     "The logo, organisation name, footer logo and browser tab icon are stored in PCPB Website Settings and rendered in the header and footer of every page. Use a PNG or SVG with a transparent background."),
    ("PCPB Website Integration", "Set the deployment mode and the portals", "Update Settings", "Open Integration Settings", "PCPB Website Integration", 0,
     "Choose how the website and the ERP are hosted. On a website server enter the ERP address and the API key of the integration user, then run Test Connection. List the customer and supplier portals with their addresses. See [Hosting](%s)." % GUIDE),
    ("PCPB Website Contact", "Enter the contact details, offices and translation languages", "Update Settings", "Open Website Settings", "PCPB Website Settings", 0,
     "Address, phone, email, opening hours, map coordinates and regional offices feed the footer and the Contact section. The Header tab holds the notices ticker and the languages offered by the Translate button."),
    ("PCPB Website Theme", "Set the theme", "Go to Page", "Open Theme", "/page-builder?panel=theme", 0,
     "Colours, fonts, corner radius and page width are CSS variables written from PCPB Website Settings. One theme applies to every page; the preview updates as you choose."),
    ("PCPB Website Menu", "Build the menu, footer and short addresses", "Go to Page", "Open Menu", "/page-builder?panel=menu", 0,
     "The menu and footer are the standard Website Settings tables (Top Bar Items, Footer Items). Short addresses are standard Route Redirects, for example jobs to /careers."),
    ("PCPB Website Pages", "Edit and publish a page", "Go to Page", "Open the Website Builder", "/page-builder", 0,
     "A page is a standard Web Page made of sections (Web Templates). Drag sections in, edit them, save a draft, then publish through the Web Page workflow. Visitors see a change only after it is published."),
    ("PCPB Website Roles", "Assign website roles to users", "Go to Page", "Open Users", "user", 1,
     "Website Manager administers settings, theme, menu and integration. Website Content Editor drafts, Website Content Approver reviews and Website Publisher publishes. The approval steps are the Workflow named PCPB Web Page Publishing."),
    ("PCPB Website Registers", "Publish registers and other ERP records", "Go to Page", "Open Registers", "pcpb-register", 1,
     "A register exposes one ERP record type to the public: you set the filter that decides which records are public and tick the fields that may be shown. A register can have its own address (for example /memos) and a Publish on Website tick on the source record."),
    ("PCPB Website Posts", "Publish a news post or notice", "Create Entry", "New Post", "PCPB Post", 1,
     "Posts feed the News sections and the notices ticker. Each post has its own address and goes through the PCPB Post approval workflow."),
    ("PCPB Website Guide", "Read the administrator guide", "View Docs", "Open the Guide", GUIDE, 1,
     "How the site is structured, where each address is served from, hosting, and how to add sections and registers."),
]

def scrub(n): return n.lower().replace(" ", "_")

for folder in ("onboarding_step", "module_onboarding"):
    p = os.path.join(MOD, folder)
    if os.path.isdir(p): shutil.rmtree(p)
    os.makedirs(p)
for i, (name, title, action, label, target, optional, desc) in enumerate(STEPS, 1):
    d = {"action": action, "action_label": label, "creation": "2026-11-15 09:00:00", "description": desc, "docstatus": 0,
         "doctype": "Onboarding Step", "idx": i, "is_complete": 0, "is_single": 0, "is_skipped": 0, "modified": "2026-11-15 09:00:00",
         "modified_by": "Administrator", "name": name, "owner": "Administrator", "show_form_tour": 0, "show_full_form": 1, "title": title,
         "validate_action": 0}
    if action == "Update Settings": d.update(reference_document=target, is_single=1)
    elif action == "Create Entry": d.update(reference_document=target)
    else: d["path"] = target
    f = os.path.join(MOD, "onboarding_step", scrub(name)); os.makedirs(f)
    json.dump(d, open(os.path.join(f, scrub(name) + ".json"), "w"), indent=1)
f = os.path.join(MOD, "module_onboarding", scrub(NAME)); os.makedirs(f)
json.dump({"allow_roles": [{"role": "Website Manager"}, {"role": "System Manager"}], "creation": "2026-11-15 09:00:00", "docstatus": 0,
           "doctype": "Module Onboarding", "idx": 0, "is_complete": 0, "modified": "2026-11-15 09:00:00", "modified_by": "Administrator",
           "module": "PCPB Website", "name": NAME, "owner": "Administrator",
           "steps": [{"is_optional": s[5], "step": s[0]} for s in STEPS], "title": "Set up the PCPB website"},
          open(os.path.join(f, scrub(NAME) + ".json"), "w"), indent=1)
print(len(STEPS), "steps written")
