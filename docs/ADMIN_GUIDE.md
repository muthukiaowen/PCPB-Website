# PCPB website: administrator guide

For the ICT officer who holds the **Website Manager** role. Content staff do not need this guide; they only edit and publish pages.

## 1. What is installed
`pcpb_website` is a Frappe app on the PCPB ERP bench. It adds no parallel CMS: it uses the standard Website records and adds a visual editor on top.

| Thing | Standard record it uses | Where you manage it |
|---|---|---|
| Page | Web Page (content type Page Builder) | `/page-builder` |
| Section of a page | Web Page Block + Web Template | `/page-builder`; designs in Desk > Web Template |
| Menu, footer, short addresses, home page | Website Settings | `/page-builder` > Menu, or Desk > Website Settings |
| Approval | Workflow on Web Page (`PCPB Web Page Publishing`) | Desk > Workflow |
| Set-up guide | Module Onboarding + Onboarding Step | Desk > PCPB Website > Help > Edit the set-up guide steps |
| This guide and the read me | Help Article (category `PCPB Website Administration`) | Desk > PCPB Website > Help > Edit the guide and read me |
| Logo, contact, theme, ticker, translation | PCPB Website Settings | Desk, or `/page-builder` |
| Hosting, ERP API, portals | PCPB Website Integration | Desk > Integration settings |
| Public lists of ERP records | PCPB Register | Desk > Registers |

## 2. Roles
Install creates the roles if they are missing and adds the permissions they need. It never removes a permission.

| Role | Can |
|---|---|
| Website Manager | everything below, plus settings, theme, menu, integration, registers, onboarding steps |
| Website Content Editor | create and edit pages and posts, save drafts, submit for review |
| Website Content Approver | approve or send back |
| Website Publisher | publish and withdraw |
| PCPB Website Integration | API user of a separately hosted website; no Desk access |

Assign roles in Desk > User. To change who may do what, edit the Workflow, not the code.

## 3. First set-up
Open the **PCPB Website** workspace in the Desk. The set-up guide at the top lists the steps in order; each step opens the right screen. The same guide is in `/page-builder` under **Getting started**. To reword a step, or add one, edit the Onboarding Step record.

## 4. Pages and sections
- A page is a list of sections. Each section is a Web Template (Jinja HTML plus a field list) and the values typed into it.
- Editors work at `/page-builder`: drag a section in, **Edit**, **Duplicate**, **Hide**, **Remove**, reorder under **Page order**. Hovering a section shows its name and what it does. **Duplicate** in the page list copies a whole page as a new draft.
- The builder opens in **Build**: links and forms on the page do nothing. **Live** shows the page as a visitor sees it; links open in a new tab.
- **Save and send for approval** saves and applies the workflow action that leaves the first state. The builder reads it from the Workflow; rename or re-route the steps there.
- Cards, Leadership and News sections have **Layout > Carousel**.
- **Logo**: upload it under Logo and name. With **Use this logo in the Desk as well** ticked it also becomes the PCPB Website icon on the Desk home screen and the Desk and sign-in logo. A Desk logo set by hand in Navbar Settings is left alone.
- Saving stores a draft in `Web Page.pcpb_draft`. The draft replaces the live sections when the workflow reaches a state that sets `published = 1`.
- **New section design**: Desk > Web Template > New, type *Section*. Add fields and write the template. It appears in the builder at once. Shipped designs are in `pcpb_website/pcpb_website/web_template/`.
- Extra CSS for the whole site: PCPB Website Settings > Theme > Extra CSS.

## 5. Publishing ERP records on the website
A **PCPB Register** exposes one ERP record type to the public, read live. Nothing is copied.

1. Desk > Registers > New. Set the title and **Records Of** (the DocType).
2. **Which Records Are Public**: a filter in JSON, for example `{"status": "Registered"}`. Nothing is shown until it is set. Or press **Add a Publish on Website tick to this record type**: this adds a Custom Field `publish_on_website` to the DocType and uses it as the filter, so staff publish a record by ticking it on the ERP form.
3. Press **List all fields of the record type** and tick the fields the public may see. Long text fields show as the body of the record page; attachments show as download buttons (public files only).
4. Optional **Own Address**: `memos` serves the list at `/memos` and each record at `/memos/<record>`.
5. Tick **Published**.

Example, memos: create a register on the Memo DocType with Own Address `memos`, add the Publish on Website tick, and tick the subject, date, body and attachment fields. A memo then appears at `/memos` when someone ticks Publish on Website on it.

Guests reach these records only through `pcpb_website.api`, which enforces the filter and the ticked fields and limits requests per visitor.

## 6. Hosting and integration
Desk > Integration settings. Deployment Mode is *Single server*, *Website server (ERP hosted separately)* or *ERP server (website hosted separately)*. A website server calls the ERP with a standard Frappe API key of the integration user. The Portals table lists the customer and supplier portals and their addresses. Full steps: the Hosting article.

## 7. Translation
The site is written once, in English. The Translate button loads Google Translate when a visitor picks a language. Languages offered: PCPB Website Settings > Header. Register data is marked `translate="no"`.

## 8. Updating the app
    cd ~/frappe-bench/apps/pcpb_website && git pull
    cd ~/frappe-bench
    bench --site <site> migrate
    bench build --app pcpb_website
    bench --site <site> clear-cache

Migrate creates anything that is missing and never overwrites pages, menus, settings, onboarding steps or help articles that staff have changed.

## 9. When something looks wrong
| Symptom | Check |
|---|---|
| A section is missing on the public page | Desk > Error Log, title starts `PCPB Website: section`. The page keeps working without the failed section. |
| A register shows nothing | The filter is empty or matches no record; a ticked field no longer exists on the DocType. |
| Registers empty on a website server | Integration settings > Test Connection. |
| Translate says unavailable | The visitor's network blocks translate.google.com. |
| A change is not visible | It is a draft. Publish it; then `bench --site <site> clear-cache` if it still does not show. |
