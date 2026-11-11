# pcpb_website

The public website of the Pest Control Products Board, built on the Frappe Website module of the PCPB ERP.

## The idea in one paragraph

A page is a standard **Web Page**. A page is made of **sections**, and every section is a standard **Web Template**.
Website staff open `/page-builder`, drag sections onto the page, type into them and drop pictures in. Sections that
show ERP data (registers, tenders, vacancies, services, news, leadership, documents, forms) read it live, so the
website never holds a second copy. Menu, footer and short addresses are the standard **Website Settings** tables.
Approval is a standard **Workflow** on Web Page. Colours, fonts and shape are one Theme tab. The logo, name and
browser icon are uploaded under **Logo and name**. The site is written once, in English; a **Translate** button lets
visitors read it in other languages through Google Translate. Nothing is hardcoded.

## Where each address ends up

| Address | What answers it | Where the content is kept |
|---|---|---|
| `/` and every page (`/about-us`, `/tenders`, ...) | Web Page built from sections | Page builder |
| `/registers/<register>` and `/registers/<register>/<record>` | PCPB Register | The ERP record type the register names (Product, Premises, ...), read live |
| `/online-services/<service>` | Service + PCPB Service Profile | Portal Service records; Apply goes to the portal |
| `/tenders/<tender>` | PCPB Tender | Desk > Tenders |
| `/news/<post>` | PCPB Post | Desk > News and notices |
| `/jobs/...` | HR Job Opening (standard HRMS page) | HR; applications become Job Applicants |
| `/jobs`, `/vacancies` | forwards to `/careers` | Website Settings > Route Redirects (editable in the builder) |
| `/contact` | standard Frappe contact form | Contact Us Settings |
| `/search?q=` | all published registers, pages, posts, tenders | live |
| `/portal`, `/login`, `/signup`, `/apply`, `/verify`, `/services`, `/home`, `my-*` | the pcpb portal, untouched | pcpb app |

## Hosting

The website, the ERP and the portals can share one server or be hosted apart. All of it is set in
**Desk > PCPB Website > Integration settings**: the Deployment Mode, the ERP API connection (standard Frappe API key)
and the list of portals (customer, supplier) with their addresses. See `docs/HOSTING.md`.

## First time here

Open the **PCPB Website** workspace in the Desk: the set-up guide at the top lists the steps in order (it is a standard
Module Onboarding, editable in Desk > Onboarding Step). The same guide is in `/page-builder` under **Getting started**.
The administrator guide, written for the ICT officer holding the Website Manager role, is at `/website-guide` and is kept
as standard Help Articles (`docs/ADMIN_GUIDE.md` is its starting text).

## Changing the guides

| Guide | Where it lives | How to change it |
|---|---|---|
| Set-up guide (the steps on the workspace and under Getting started) | Onboarding Step records | Desk > PCPB Website > Help > Edit the set-up guide steps |
| Administrator, hosting and editor guides, and the site's copy of this read me | Help Article records | Desk > PCPB Website > Help > Edit the guide and read me |
| This file on GitHub | `README.md` in the repository | Edit the file and commit; it is what a new install starts from |

The site's copies are created once at install and never overwritten afterwards, so edits made in the Desk are kept.

## Install

    bench get-app https://github.com/muthukiaowen/PCPB-Website.git
    bench --site <site> install-app pcpb_website
    bench --site <site> migrate
    bench build --app pcpb_website
    bench --site <site> clear-cache

Install creates the pages, menu, footer, registers, roles and workflows once. After that it never overwrites what
staff change. Test sites only: `bench --site <site> execute pcpb_website.install.seed_demo` adds sample records.

## For developers

- `pcpb_website/overrides.py` Web Page inside the PCPB design; the draft goes live on publish
- `pcpb_website/render.py` sections to HTML
- `pcpb_website/builder.py` API behind `/page-builder`
- `pcpb_website/api.py` public register API (field and filter whitelisted, rate limited, fail closed)
- `pcpb_website/shell.py` which website pages wear the PCPB header and footer
- `pcpb_website/remote.py` the link between a website server and an ERP server hosted apart
- `pcpb_website/pcpb_website/web_template/` the section library (JSON fields + Jinja HTML per section)
- `pcpb_website/sections.json` catalogue text for the builder; `starter_site.json` first pages; `page_presets.json`
- A new section = a new Web Template (in Desk, or a folder here). It appears in the builder by itself.

See `docs/TECHNICAL.md`, `docs/ADMIN_GUIDE.md`, `docs/HOSTING.md` and `docs/EDITOR_GUIDE.md`.
