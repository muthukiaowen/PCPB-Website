# Hosting the website, the ERP and the portals

Everything about where things are hosted is in one place: **Desk > PCPB Website > Integration settings**.

## Deployment Mode

| Mode | Use it when | What this site does |
|---|---|---|
| Single server (website and ERP together) | one site runs everything (the default) | reads registers, services and vacancies from its own records |
| Website server (ERP hosted separately) | this site is the public website | calls the ERP API for registers, services and vacancies |
| ERP server (website hosted separately) | this site is the ERP | answers the website's API calls; shows no public website |

The PCPB Website app is installed on both servers. Each server gets its own Deployment Mode.

## Connecting a website server to the ERP

The connection uses the standard Frappe API key, the same mechanism as any other integration.

**On the ERP server**

    bench --site <erp-site> set-config pcpb_website_role provider
    bench --site <erp-site> install-app pcpb_website

1. Open Integration settings. Deployment Mode is already *ERP server*.
2. Press **Create Integration User and API Keys**. Copy the API Key and API Secret (the secret is shown once).

The integration user holds one role, **PCPB Website Integration**. It cannot open the Desk and can read nothing beyond the
public register, service and vacancy data. Its keys can be reissued at any time, here or under User > Settings > API Access.

**On the website server**

1. Integration settings > Deployment Mode: *Website server (ERP hosted separately)*.
2. Enter the **ERP Address**, the **API Key** and the **API Secret**.
3. Press **Test Connection**. The result and the time are recorded on the form.

| Setting | Meaning |
|---|---|
| Cache Duration | how long an ERP answer is reused before asking again (120 seconds to start with; 0 = off) |
| Request Timeout | how long to wait for the ERP before falling back to the last good answer |

### What is kept where
| Website server | ERP server |
|---|---|
| Pages, sections, theme, menu, footer | Registers (which records and fields are public) |
| News and notices, tenders, documents, leadership | Products, premises and every other register record |
| Logo, contact details, wording | Services and their website descriptions |
| | Job openings and job applications (HR) |

### How a request travels
A visitor's browser talks only to the website server. The website server calls the ERP API with its key, caches the answer
for the Cache Duration, and if the ERP cannot be reached shows the last good answer, so a short ERP outage does not empty
the website. Only already-public data is exchanged. Without a valid key the ERP still answers, but treats the website server
as a single visitor and limits its requests; with the key it does not. The ERP must accept HTTPS from the website server.

## Portals

The **Portals** table in Integration settings lists every portal the public is sent to.

| Column | Meaning |
|---|---|
| Portal Name | shown on the website, e.g. Customer Portal, Supplier Portal |
| Audience | *Customers and applicants*, *Suppliers* or *Other*; one enabled portal per audience |
| Address | empty = the portal is on the ERP site (or on this site in Single server mode); otherwise its own address |
| Sign-in, Registration, Home, Verification pages | the paths on that portal |
| Show in Website Header | whether the header links to it |

- **Customer portal**: Sign in, Create an account, Apply and Verify a certificate go here.
- **Supplier portal**: linked in the header and offered on open tender pages. It is listed but switched off until its address
  and pages are confirmed.
- Vacancies open the HR job page on the ERP, where the application form is.
