# PCPB website: technical notes

For developers and the ICT officer. What the app is built from, what install changes on a site, and what is not yet done.

## Standard Frappe pieces used
Web Page, Web Page Block, Web Template, Website Settings (Top Bar Items, Footer Items, Route Redirects, Home Page),
Workflow, Web Form, Contact Us Settings, Help Article, Module Onboarding, Onboarding Step, Desktop Icon, Workspace Sidebar,
Custom Field, Custom DocPerm, HRMS Job Opening pages.

Custom Fields added: `Web Page.pcpb_draft` (the draft the builder saves until the page is published) and, only when a
manager presses the button on a register, `publish_on_website` on that register's source record type.

## Pages and the builder
A page is a standard Web Page whose sections are Web Page Blocks, each drawn by a Web Template. `/page-builder` edits them.
- **Build and Live**: in Build no link or form on the page does anything, so staff only build. Live shows the page as a
  visitor sees it and opens links in a new tab.
- **Drafts**: saving stores the sections in `Web Page.pcpb_draft`. Visitors keep seeing the published version.
- **Approval**: the steps are the Workflow record **PCPB Web Page Publishing** (Draft, In Review, Approved, Published,
  Withdrawn). **Save and send for approval** saves and applies the workflow action that leaves the first state; the builder
  reads that action from the Workflow and assumes nothing about its name. The draft replaces the live sections when the
  page reaches a state that sets `published = 1`. Change the steps in Desk > Workflow, not in code.
- **Carousel**: Cards, Leadership and News sections have a Layout choice; Carousel scrolls sideways with arrows, swipe and
  optional automatic movement (it stops when the visitor asks the device for reduced motion).

## Roles
Website Manager (standard; created if missing), Website Content Editor, Website Content Approver, Website Publisher,
PCPB Website Integration (API user of a separately hosted website). Install only adds permissions, never removes them.

## Logo
The logo uploaded in the builder (Logo and name) or in PCPB Website Settings is used in the website header and, when
**Use this logo in the Desk as well** is ticked, on the PCPB Website icon of the Desk home screen and as the logo of the
Desk and the sign-in page (Navbar Settings and Website Settings > App Logo). A Desk logo chosen separately by hand is left alone.

## Translation
One language of record, English. The Translate button loads Google Translate only after a visitor picks a language,
remembers the choice, and notes that the English text is the official version. Register data is marked `translate="no"`.

## Registers
A PCPB Register publishes any ERP record type as a public list with search, filters, CSV and a record page, optionally
at its own address (for example `/memos`). Only listed fields and filters are ever returned; anything else is refused.

## Hosting, ERP API and portals
One record, **PCPB Website Integration**: Deployment Mode, the ERP API connection (standard API key and secret), and the
table of portals (customer, supplier). See `docs/HOSTING.md`.

## Guides
- Set-up guide: Module Onboarding `PCPB Website Onboarding` and its Onboarding Steps, shown on the workspace and in the builder.
- Administrator, hosting and editor guides and the read me: Help Articles in the category `PCPB Website Administration`
  (unpublished, staff only), read at `/website-guide`. Created once from `README.md` and `docs/`; edits in the Desk are kept.

## What install changes outside this app
- Website Settings: home page set to `site` (only if it was empty, `home`, `login` or `site`), menu and footer filled once, redirects added.
- Contact Us Settings: the standard contact form is switched on.
- Web Page: the content roles may create and edit (Custom DocPerm); a workflow is added if Web Page has none.
- Hooks: `/` shows Website Settings > Home Page; every Web Page shows inside the PCPB design.
- The portal addresses listed in Settings > Where the design applies are never touched.

## Not done, and why
- No memo register is created, because the ERP's memo record type and field names are not confirmed. Creating one takes a
  few minutes (administrator guide, Registers).
- Registers for restricted, withdrawn and banned lists are not created, for the same reason.
- The supplier portal row is created switched off until its address and pages are confirmed.
- Not checked on the test bench (it blocks the outside services): the translated page itself, the OpenStreetMap map,
  email from the contact form. Also not checked: the real pcpb app and UAT data (a stand-in was used).
