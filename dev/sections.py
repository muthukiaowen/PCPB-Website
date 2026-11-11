"""Dev helper: writes the section library (standard Web Templates) and sections.json (builder catalogue).
Run:  python3 -I sections.py
"""
import datetime
import json, os, shutil

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pcpb_website")
OUT = os.path.join(APP, "pcpb_website", "web_template")
ICONS = "leaf\nsprout\nshield\nflask\nalert\nclock\ngrid\nlimit\nban\ndoc\nbuilding\nsearch\nusers\nbriefcase\npin\nphone\nmail\ndownload\nmegaphone\ngavel\nscale\nbook\nglobe\ncheck\nform\nimage\nstar"
S = []


def f(name, ftype, label, options=None, default=None):
    d = {"fieldname": name, "fieldtype": ftype, "label": label, "reqd": 0}
    if options: d["options"] = options
    if default is not None: d["default"] = default
    return d


def sec(name, category, description, icon, fields, html, order, data=""):
    S.append(dict(name=name, category=category, description=description, icon=icon, fields=fields, html=html.strip() + "\n", order=order, data=data))


HEAD = """{% if title or subtitle %}<div class="pc-head"><h2>{{ title or '' }}</h2>{% if view_all_url %}<a class="pc-link" href="{{ lurl(view_all_url) }}">{{ view_all_label or tr('view_all') }} {{ icon('arrow') }}</a>{% endif %}{% if subtitle %}<p>{{ subtitle }}</p>{% endif %}</div>{% endif %}"""
TITLE = [f("title", "Data", "Heading"), f("subtitle", "Small Text", "Text under the heading")]
VIEWALL = [f("view_all_label", "Data", "Link label (e.g. View all)"), f("view_all_url", "Data", "Link address")]

# ------------------------------------------------------------------ layout
sec("PCPB Hero", "Layout", "Large opening banner with heading, buttons and the optional product status check box.", "star", [
    f("eyebrow", "Data", "Small line above the heading"), f("title", "Data", "Heading"), f("text", "Small Text", "Text"),
    f("image", "Attach Image", "Background picture (optional)"),
    f("button_1_label", "Data", "First button label"), f("button_1_url", "Data", "First button address"),
    f("button_2_label", "Data", "Second button label"), f("button_2_url", "Data", "Second button address"),
    f("sb_check", "Section Break", "Status check box"),
    f("show_check", "Check", "Show the product status check", default="1"),
    f("check_title", "Data", "Box heading"), f("check_text", "Small Text", "Box text"), f("check_placeholder", "Data", "Search box hint"),
    f("check_chips", "Small Text", "Example searches (one per line)"),
], """
<div class="pc-hero{{ ' has-img' if image }}"{% if image %} style="--pc-img:url('{{ image }}')"{% endif %}>
  <div class="pc-wrap pc-hero-grid{{ '' if show_check else ' one' }}">
    <div>{% if eyebrow %}<span class="pc-eyebrow">{{ eyebrow }}</span>{% endif %}
      <h1>{{ title or '' }}</h1>{% if text %}<p class="pc-lead">{{ text }}</p>{% endif %}
      <div class="pc-btn-row">{% if button_1_label %}<a class="pc-btn gold" href="{{ lurl(button_1_url) }}">{{ button_1_label }} {{ icon('arrow') }}</a>{% endif %}
        {% if button_2_label %}<a class="pc-btn ghost" href="{{ lurl(button_2_url) }}">{{ button_2_label }}</a>{% endif %}</div></div>
    {% if show_check %}<div class="pc-glass" data-pc-check data-none="{{ tr('check_none') }}" data-more="{{ tr('view_all') }}">
      <h2>{{ icon('shield') }} {{ check_title or tr('status_check') }}</h2>{% if check_text %}<p>{{ check_text }}</p>{% endif %}
      <form class="pc-searchbox" action="/search" method="get">{{ icon('search') }}<input type="search" name="q" placeholder="{{ check_placeholder or tr('search') }}" autocomplete="off" aria-label="{{ tr('search') }}"><button class="pc-btn primary sm" type="submit">{{ tr('check') }}</button></form>
      {% if check_chips %}<div class="pc-chips">{% for c in lines(check_chips) %}<a class="pc-chip" href="/search?q={{ c | urlencode }}">{{ c }}</a>{% endfor %}</div>{% endif %}
      <div class="pc-hits" aria-live="polite"></div></div>{% endif %}
  </div>
</div>""", 10)

sec("PCPB Page Header", "Layout", "Coloured title band for the top of an inside page, with the breadcrumb trail.", "square", [
    f("title", "Data", "Page heading"), f("text", "Small Text", "Text under the heading"),
    f("image", "Attach Image", "Background picture (optional)"), f("show_crumbs", "Check", "Show the breadcrumb trail", default="1"),
], """
<div class="pc-pagehead{{ ' has-img' if image }}"{% if image %} style="--pc-img:url('{{ image }}')"{% endif %}><div class="pc-wrap">
  {% if show_crumbs %}<nav class="pc-crumbs" aria-label="Breadcrumb"><a href="{{ lurl('/') }}">{{ tr('home') }}</a><span>&rsaquo;</span><span>{{ title or '' }}</span></nav>{% endif %}
  <h1>{{ title or '' }}</h1>{% if text %}<p class="pc-lead">{{ text }}</p>{% endif %}
</div></div>""", 20)

sec("PCPB Slider", "Layout", "Rotating slides with a picture, heading, text and a button each.", "image", [
    f("seconds", "Int", "Seconds per slide", default="6"),
    f("slides", "Table Break", "Slides"),
    f("image", "Attach Image", "Picture"), f("title", "Data", "Heading"), f("text", "Small Text", "Text"),
    f("button_label", "Data", "Button label"), f("button_url", "Data", "Button address"),
], """
<div class="pc-wrap pc-pad" style="padding-bottom:0">
<div class="pc-slider" data-pc-slider="{{ seconds or 6 }}" aria-roledescription="carousel">
  {% for s in slides or [] %}<div class="pc-slide{{ ' on' if loop.first }}"{% if s.image %} style="--pc-img:url('{{ s.image }}')"{% endif %}><div>
    <h2>{{ s.title or '' }}</h2>{% if s.text %}<p>{{ s.text }}</p>{% endif %}
    {% if s.button_label %}<a class="pc-btn gold sm" href="{{ lurl(s.button_url) }}">{{ s.button_label }} {{ icon('arrow') }}</a>{% endif %}</div></div>{% endfor %}
  {% if (slides or []) | length > 1 %}<button type="button" class="pc-slider-nav prev" aria-label="{{ tr('previous') }}">&lsaquo;</button><button type="button" class="pc-slider-nav next" aria-label="{{ tr('next') }}">&rsaquo;</button>
  <div class="pc-dots">{% for s in slides %}<button type="button" class="{{ 'on' if loop.first }}" aria-label="{{ loop.index }}"></button>{% endfor %}</div>{% endif %}
  {% if not slides %}<div class="pc-slide on"><div><h2>{{ tr('slider_empty') }}</h2></div></div>{% endif %}
</div></div>""", 30)

# ------------------------------------------------------------------ content
sec("PCPB Text", "Content", "A heading and formatted text: paragraphs, lists, links, pictures and tables.", "doc", TITLE[:1] + [
    f("content", "Markdown Editor", "Text"), f("wide", "Check", "Use the full page width"), f("center", "Check", "Centre the text"),
], """
<div class="pc-wrap pc-pad"><div class="pc-prose{{ ' wide' if wide }}{{ ' pc-center' if center }}"{% if center %} style="margin:0 auto"{% endif %}>
  {% if title %}<h2>{{ title }}</h2>{% endif %}{{ md(content) }}</div></div>""", 40)

sec("PCPB Cards", "Content", "Cards or tiles with an icon or picture, text and a link. As a grid or a carousel.", "grid", TITLE + VIEWALL + [
    f("columns", "Select", "Cards per row", "2\n3\n4", "3"),
    f("layout", "Select", "Layout", "Grid\nCarousel", "Grid"), f("autoplay", "Check", "Carousel moves by itself"),
    f("cards", "Table Break", "Cards"),
    f("icon", "Select", "Icon", ICONS), f("image", "Attach Image", "Picture (instead of the icon)"),
    f("title", "Data", "Card heading"), f("text", "Small Text", "Card text"),
    f("link_label", "Data", "Link label"), f("url", "Data", "Link address"),
], """
<div class="pc-wrap pc-pad">""" + HEAD + """
  <div class="{{ 'pc-track' if layout == 'Carousel' else 'pc-grid' }}"{% if layout == 'Carousel' %} data-pc-carousel="{{ 5 if autoplay else 0 }}"{% endif %} style="--cols:{{ columns or 3 }}">
  {% for c in cards or [] %}<{{ 'a href="' ~ lurl(c.url) ~ '"' if c.url else 'div' }} class="pc-card">
    {% if c.image %}<img class="pc-card-img" src="{{ c.image }}" alt="">{% elif c.icon %}<span class="pc-card-ic">{{ icon(c.icon) }}</span>{% endif %}
    <h3>{{ c.title or '' }}</h3>{% if c.text %}<p>{{ c.text }}</p>{% endif %}
    {% if c.url %}<span class="pc-more">{{ c.link_label or tr('read_more') }} {{ icon('arrow') }}</span>{% endif %}
  </{{ 'a' if c.url else 'div' }}>{% endfor %}
  </div>{% if not cards %}<div class="pc-empty">{{ tr('cards_empty') }}</div>{% endif %}</div>""", 50)

sec("PCPB Image and Text", "Content", "A picture beside a heading, text and a button.", "image", [
    f("title", "Data", "Heading"), f("content", "Markdown Editor", "Text"), f("image", "Attach Image", "Picture"),
    f("image_alt", "Data", "Picture description"), f("image_side", "Select", "Picture side", "Right\nLeft", "Right"),
    f("button_label", "Data", "Button label"), f("button_url", "Data", "Button address"),
], """
<div class="pc-wrap pc-pad"><div class="pc-split{{ ' rev' if image_side == 'Left' }}">
  <div class="pc-prose">{% if title %}<h2>{{ title }}</h2>{% endif %}{{ md(content) }}
    {% if button_label %}<div class="pc-btn-row"><a class="pc-btn primary" href="{{ lurl(button_url) }}">{{ button_label }} {{ icon('arrow') }}</a></div>{% endif %}</div>
  <div>{% if image %}<img src="{{ image }}" alt="{{ image_alt or '' }}">{% else %}<div class="pc-empty">{{ tr('image_empty') }}</div>{% endif %}</div>
</div></div>""", 60)

sec("PCPB Numbers", "Content", "A row of key figures (for example: products registered, premises licensed).", "check", [
    f("lift", "Check", "Overlap the section above"),
    f("stats", "Table Break", "Figures"), f("number", "Data", "Figure"), f("label", "Data", "What it counts"),
    f("register", "Link", "Or count the records of this register", "PCPB Register"),
], """
<div class="pc-wrap {{ 'pc-statlift' if lift else 'pc-pad' }}"{% if lift %} style="margin-top:-34px;position:relative;z-index:2;padding-bottom:8px"{% endif %}>
  <dl class="pc-stats" style="--cols:{{ [(stats or []) | length, 4] | min or 1 }}">{% for s in stats or [] %}{% set n = register_count(s.register) if s.register else None %}
    <div><dt>{{ s.label or '' }}</dt><dd>{{ n if n is not none else (s.number or '') }}</dd></div>{% endfor %}</dl></div>""", 70, data="Registers")

sec("PCPB Call to Action", "Content", "A highlighted band with a short message and a button.", "megaphone", [
    f("title", "Data", "Heading"), f("text", "Small Text", "Text"), f("button_label", "Data", "Button label"), f("button_url", "Data", "Button address"),
    f("style", "Select", "Colour", "Green\nGold\nLight", "Green"),
], """
<div class="pc-wrap pc-pad"><div class="pc-cta {{ (style or 'Green') | lower }}"><div><h2>{{ title or '' }}</h2>{% if text %}<p>{{ text }}</p>{% endif %}</div>
  {% if button_label %}<a class="pc-btn {{ 'primary' if style in ('Gold', 'Light') else 'gold' }}" href="{{ lurl(button_url) }}">{{ button_label }} {{ icon('arrow') }}</a>{% endif %}</div></div>""", 80)

sec("PCPB Tabs", "Content", "Several panels of text; the visitor switches between them with tabs.", "grid", TITLE[:1] + [
    f("tabs", "Table Break", "Tabs"), f("label", "Data", "Tab name"), f("content", "Markdown Editor", "Tab text"),
], """
<div class="pc-wrap pc-pad">{% if title %}<div class="pc-head"><h2>{{ title }}</h2></div>{% endif %}
  <div data-pc-tabs><div class="pc-tabs-bar" role="tablist">{% for t in tabs or [] %}<button type="button" class="pc-tab" role="tab" aria-selected="{{ 'true' if loop.first else 'false' }}">{{ t.label or loop.index }}</button>{% endfor %}</div>
  {% for t in tabs or [] %}<div class="pc-prose wide" role="tabpanel"{% if not loop.first %} hidden{% endif %}>{{ md(t.content) }}</div>{% endfor %}</div></div>""", 90)

sec("PCPB Questions and Answers", "Content", "A list of questions that open to show the answer.", "check", TITLE + [
    f("items", "Table Break", "Questions"), f("question", "Data", "Question"), f("answer", "Markdown Editor", "Answer"),
], """
<div class="pc-wrap pc-pad pc-narrow">""" + HEAD.replace("{% if view_all_url %}", "{% if false %}") + """
  {% for i in items or [] %}<details class="pc-acc"><summary>{{ i.question or '' }}</summary><div>{{ md(i.answer) }}</div></details>{% endfor %}</div>""", 100)

sec("PCPB Gallery", "Content", "A grid of photographs that open large when clicked.", "image", TITLE + [
    f("images", "Table Break", "Pictures"), f("image", "Attach Image", "Picture"), f("caption", "Data", "Caption"),
], """
<div class="pc-wrap pc-pad">""" + HEAD.replace("{% if view_all_url %}", "{% if false %}") + """
  <div class="pc-gallery" data-pc-gallery>{% for g in images or [] %}{% if g.image %}<figure><img src="{{ g.image }}" alt="{{ g.caption or '' }}" loading="lazy">{% if g.caption %}<figcaption>{{ g.caption }}</figcaption>{% endif %}</figure>{% endif %}{% endfor %}</div>
  {% if not images %}<div class="pc-empty">{{ tr('gallery_empty') }}</div>{% endif %}</div>""", 110)

sec("PCPB Custom HTML", "Content", "For ICT staff: your own HTML. Jinja is allowed.", "form", [
    f("html", "Text", "HTML"), f("contained", "Check", "Keep inside the page width", default="1"),
], """
{% if contained %}<div class="pc-wrap pc-pad">{{ html or '' }}</div>{% else %}{{ html or '' }}{% endif %}""", 120)

# ------------------------------------------------------------------ live data from the ERP
sec("PCPB Register Search", "Live data", "A search box that checks every public register at once.", "search", TITLE + [
    f("placeholder", "Data", "Search box hint"), f("chips", "Small Text", "Example searches (one per line)"),
], """
<div class="pc-wrap pc-pad pc-narrow pc-center">{% if title %}<h2>{{ title }}</h2>{% endif %}{% if subtitle %}<p class="pc-muted">{{ subtitle }}</p>{% endif %}
  <div data-pc-check data-none="{{ tr('check_none') }}" data-more="{{ tr('view_all') }}">
  <form class="pc-searchbox big" action="/search" method="get">{{ icon('search') }}<input type="search" name="q" placeholder="{{ placeholder or tr('search') }}" autocomplete="off" aria-label="{{ tr('search') }}"><button class="pc-btn primary" type="submit">{{ tr('search') }}</button></form>
  {% if chips %}<div class="pc-chips" style="justify-content:center">{% for c in lines(chips) %}<a class="pc-chip" href="/search?q={{ c | urlencode }}">{{ c }}</a>{% endfor %}</div>{% endif %}
  <div class="pc-hits" aria-live="polite"></div></div></div>""", 200, data="Registers")

sec("PCPB Register Index", "Live data", "Cards for every public register, grouped. New registers appear here by themselves.", "grid", TITLE + [
    f("group", "Link", "Only this group (empty = all)", "PCPB Register Group"), f("show_counts", "Check", "Show how many records each holds", default="1"),
    f("columns", "Select", "Cards per row", "2\n3\n4", "3"),
], """
<div class="pc-wrap pc-pad">""" + HEAD.replace("{% if view_all_url %}", "{% if false %}") + """
  {% set groups = register_groups(group) %}
  {% for g in groups %}{% if g.title and groups | length > 1 %}<h3 style="margin-top:1.2em">{{ g.title }}</h3>{% if g.text %}<p class="pc-muted">{{ g.text }}</p>{% endif %}{% endif %}
  <div class="pc-grid" style="--cols:{{ columns or 3 }};margin-bottom:18px">{% for r in g['items'] %}<a class="pc-card" href="{{ r.url }}">
    <span class="pc-card-ic">{{ icon(r.icon) }}</span><h3>{{ r.title }}</h3>{% if r.text %}<p>{{ r.text }}</p>{% endif %}
    <span class="pc-more">{% if show_counts %}{% set n = register_count(r.slug) %}{% if n is not none %}<span class="pc-tag {{ {'Banned': 'bad', 'Withdrawn': 'warn', 'Restricted': 'warn'}.get(r.kind, 'ok') }}">{{ n }} {{ tr('records') }}</span>{% endif %}{% endif %} {{ tr('open_register') }} {{ icon('arrow') }}</span></a>{% endfor %}</div>{% endfor %}
  {% if not groups %}<div class="pc-empty">{{ tr('registers_empty') }}</div>{% endif %}</div>""", 210, data="Registers")

sec("PCPB Register Table", "Live data", "One register shown as a searchable table, read live from the ERP.", "grid", TITLE + [
    f("register", "Link", "Register", "PCPB Register"), f("rows", "Int", "Rows per page", default="10"),
], """
<div class="pc-wrap pc-pad">""" + HEAD.replace("{% if view_all_url %}", "{% if register %}").replace("lurl(view_all_url)", "lurl('/registers/' ~ register)") + """
  {% if register %}{% set reg_slug = register %}{% set reg_rows = rows or 10 %}{% set reg_compact = 1 %}{% include "templates/includes/pcpb_register.html" %}
  {% else %}<div class="pc-empty">{{ tr('register_pick') }}</div>{% endif %}</div>""", 220, data="Registers")

sec("PCPB Registers Strip", "Live data", "A moving strip naming every register with its record count.", "leaf", TITLE[:1], """
<div class="pc-wrap pc-pad">{% if title %}<div class="pc-head"><h2>{{ title }}</h2></div>{% endif %}
  {% set regs = registers() %}{% if regs %}<div class="pc-marquee"><div>{% for pass in (1, 2) %}{% for r in regs %}<a class="pc-mq" href="{{ r.url }}"{% if pass == 2 %} aria-hidden="true" tabindex="-1"{% endif %}>{{ icon(r.icon) }} {{ r.title }}{% set n = register_count(r.slug) %}{% if n is not none %} <b>{{ n }}</b>{% endif %}</a>{% endfor %}{% endfor %}</div></div>
  {% else %}<div class="pc-empty">{{ tr('registers_empty') }}</div>{% endif %}</div>""", 230, data="Registers")

sec("PCPB News", "Live data", "The latest news, notices and circulars. New posts appear here by themselves.", "megaphone", TITLE + VIEWALL + [
    f("types", "Select", "Which posts", "All\nNews\nNotice\nCircular\nSafety Alert\nAnnouncement\nPress Release\nEvent", "All"),
    f("limit", "Int", "How many", default="3"), f("layout", "Select", "Layout", "Cards\nList\nCarousel", "Cards"), f("autoplay", "Check", "Carousel moves by itself"),
    f("archive", "Check", "Show the archive (expired posts) instead"),
], """
<div class="pc-wrap pc-pad">""" + HEAD + """
  {% set rows = posts(types, limit or 3, archive) %}
  {% if layout == 'List' %}<div class="pc-list">{% for p in rows %}<a class="pc-row" href="{{ p.url }}" style="text-decoration:none;color:inherit"><div><small><span class="pc-tag info">{{ p.type_label }}</span> {{ p.date_text }}</small><h3>{{ p.title }}</h3>{% if p.summary %}<p>{{ p.summary }}</p>{% endif %}</div><span class="pc-link">{{ tr('read_more') }} {{ icon('arrow') }}</span></a>{% endfor %}</div>
  {% else %}<div class="{{ 'pc-track' if layout == 'Carousel' else 'pc-grid' }}"{% if layout == 'Carousel' %} data-pc-carousel="{{ 5 if autoplay else 0 }}"{% endif %}>{% for p in rows %}<a class="pc-card" href="{{ p.url }}">{% if p.hero_image %}<img class="pc-card-img" src="{{ p.hero_image }}" alt="{{ p.hero_alt or '' }}" loading="lazy">{% endif %}
    <small><span class="pc-tag info">{{ p.type_label }}</span> {{ p.date_text }}</small><h3>{{ p.title }}</h3>{% if p.summary %}<p>{{ p.summary }}</p>{% endif %}<span class="pc-more">{{ tr('read_more') }} {{ icon('arrow') }}</span></a>{% endfor %}</div>{% endif %}
  {% if not rows %}<div class="pc-empty">{{ tr('news_none') }}</div>{% endif %}</div>""", 240, data="Posts")

sec("PCPB Tenders", "Live data", "Tenders from the Tenders list. Closed ones move to the archive by themselves.", "gavel", TITLE + VIEWALL + [
    f("group", "Select", "Which tenders", "Open\nArchive\nAll", "Open"), f("limit", "Int", "How many", default="20"),
], """
<div class="pc-wrap pc-pad">""" + HEAD + """
  {% set rows = tenders(group or 'Open', limit or 20) %}
  <div class="pc-list">{% for t in rows %}<div class="pc-row"><div>
    <small><span class="pc-tag {{ {'Open': 'ok', 'Awarded': 'info', 'Cancelled': 'bad'}.get(t.status, '') }}">{{ t.status_label }}</span> {{ t.tender_no or '' }}{% if t.category %} &middot; {{ t.category }}{% endif %}</small>
    <h3><a href="{{ t.url }}" style="text-decoration:none;color:inherit">{{ t.title }}</a></h3>{% if t.summary %}<p>{{ t.summary }}</p>{% endif %}
    {% if t.closing_text %}<p><strong>{{ tr('tender_closes') }}:</strong> {{ t.closing_text }}</p>{% endif %}</div>
    <a class="pc-btn sm" href="{{ t.url }}">{{ tr('tender_view') }}</a></div>{% endfor %}</div>
  {% if not rows %}<div class="pc-empty">{{ tr('tender_none') }}</div>{% endif %}</div>""", 250, data="Tenders")

sec("PCPB Jobs", "Live data", "Open vacancies, read live from HR (Job Opening). Applying happens on the HR job page.", "briefcase", TITLE + VIEWALL + [
    f("limit", "Int", "How many", default="20"), f("empty_text", "Small Text", "Text when there are no vacancies"),
], """
<div class="pc-wrap pc-pad">""" + HEAD + """
  {% set rows = vacancies(limit or 20) %}
  <div class="pc-list">{% for v in rows %}<div class="pc-row"><div>
    <small>{{ icon('briefcase') }} {{ v.department or '' }}{% if v.employment_type %} &middot; {{ v.employment_type }}{% endif %}</small>
    <h3>{{ v.job_title or v.designation or v.name }}</h3>
    <p>{% if v.location %}{{ tr('location') }}: {{ v.location }}{% endif %}{% if v.closes_text %}{% if v.location %} &middot; {% endif %}{{ tr('closes') }}: {{ v.closes_text }}{% endif %}</p></div>
    {% if v.url %}<a class="pc-btn primary sm" href="{{ v.url }}">{{ tr('apply_job') }}</a>{% endif %}</div>{% endfor %}</div>
  {% if not rows %}<div class="pc-empty">{{ empty_text or tr('careers_none') }}</div>{% endif %}</div>""", 260, data="HR Job Openings")

sec("PCPB Leadership", "Live data", "The Board and management, from the Leadership list, as a grid or a carousel. Only current office holders show.", "users", TITLE + [
    f("groups", "Select", "Who to show", "All\nBoard Chairperson\nChief Executive Officer\nBoard Member\nExecutive Management\nDepartment Head\nOther", "All"),
    f("feature_first", "Check", "Show the first person large, with their profile"),
    f("layout", "Select", "Layout", "Grid\nCarousel", "Grid"), f("autoplay", "Check", "Carousel moves by itself"),
    f("columns", "Select", "People per row", "3\n4\n5", "4"),
], """
<div class="pc-wrap pc-pad">""" + HEAD.replace("{% if view_all_url %}", "{% if false %}") + """
  {% set rows = leaders(None if (groups or 'All') == 'All' else groups) %}
  {% if feature_first and rows %}{% set p = rows[0] %}<div class="pc-lead-person">{% if p.photo %}<img src="{{ p.photo }}" alt="{{ p.photo_alt or p.full_name }}">{% else %}<div class="pc-person"><span class="pc-ph">{{ p.full_name[:1] }}</span></div>{% endif %}
    <div class="pc-prose"><small class="pc-muted">{{ p.title }}</small><h3 style="font-size:1.4rem">{{ p.full_name }}</h3>{{ p.bio or '' }}</div></div>{% endif %}
  <div class="{{ 'pc-track' if layout == 'Carousel' else 'pc-people' }}"{% if layout == 'Carousel' %} data-pc-carousel="{{ 5 if autoplay else 0 }}"{% endif %} style="--cols:{{ columns or 4 }}">{% for p in (rows[1:] if feature_first else rows) %}<div class="pc-person">{% if p.photo %}<img src="{{ p.photo }}" alt="{{ p.photo_alt or p.full_name }}" loading="lazy">{% else %}<span class="pc-ph">{{ p.full_name[:1] }}</span>{% endif %}
    <div><h3>{{ p.full_name }}</h3><p>{{ p.title }}</p>{% if p.bio %}<details><summary>{{ tr('profile') }}</summary>{{ p.bio }}</details>{% endif %}</div></div>{% endfor %}</div>
  {% if not rows %}<div class="pc-empty">{{ tr('leaders_none') }}</div>{% endif %}</div>""", 270, data="Leadership")

sec("PCPB Services", "Live data", "The Board's online services, read live from the portal. Apply takes the visitor to the portal.", "form", TITLE + VIEWALL + [
    f("mode", "Select", "Which services", "Featured\nAll", "Featured"), f("limit", "Int", "How many (featured)", default="6"),
    f("group_by", "Check", "Group by service type (when showing all)", default="1"),
], """
<div class="pc-wrap pc-pad">""" + HEAD + """
  {% set rows = featured_services(limit or 6) if (mode or 'Featured') == 'Featured' else services() %}
  {% macro card(s) %}<div class="pc-card"><small>{{ s.group_label }}</small><h3><a href="{{ lurl('/online-services/' ~ s.slug) }}" style="text-decoration:none;color:inherit">{{ s.name }}</a></h3><p>{{ s.short }}</p>
    <div class="pc-btn-row" style="margin-top:auto"><a class="pc-btn sm" href="{{ lurl('/online-services/' ~ s.slug) }}">{{ tr('details') }}</a>{% include "templates/includes/pcpb_apply.html" %}</div></div>{% endmacro %}
  {% if mode == 'All' and group_by %}{% for grp, items in rows | groupby('group_label') %}<h3 style="margin-top:1.2em">{{ grp }}</h3><div class="pc-grid" style="margin-bottom:18px">{% for s in items %}{{ card(s) }}{% endfor %}</div>{% endfor %}
  {% else %}<div class="pc-grid">{% for s in rows %}{{ card(s) }}{% endfor %}</div>{% endif %}
  {% if not rows %}<div class="pc-empty">{{ tr('services_none') }}</div>{% endif %}</div>""", 280, data="Portal services")

sec("PCPB Downloads", "Live data", "Documents from the Documents list (forms, guidelines, reports), by category.", "download", TITLE + VIEWALL + [
    f("category", "Select", "Category", "All\nActs and Regulations\nForms\nApplication Forms\nGuidelines\nNotices\nTenders\nReports\nRegisters\nPublications\nApproved Labels\nPublic Awareness\nCitizen Service Charter\nInstitutional Documents\nStrategic Plans\nOther", "All"),
    f("limit", "Int", "How many", default="50"), f("group_by", "Check", "Group by category", default="1"),
], """
<div class="pc-wrap pc-pad">""" + HEAD + """
  {% set rows = documents(category, limit or 50) %}
  {% macro file(d) %}<a class="pc-file" href="{{ d.url }}" target="_blank" rel="noopener"><b>{{ d.ext }}</b><span>{{ d.title }}<small>{{ d.category }}{% if d.year %} &middot; {{ d.year }}{% endif %}</small></span>{{ icon('download') }}</a>{% endmacro %}
  {% if group_by and (category or 'All') == 'All' %}{% for cat, items in rows | groupby('category') %}<h3 style="margin-top:1.2em">{{ cat }}</h3><div class="pc-grid" style="--cols:2;margin-bottom:18px">{% for d in items %}{{ file(d) }}{% endfor %}</div>{% endfor %}
  {% else %}<div class="pc-grid" style="--cols:2">{% for d in rows %}{{ file(d) }}{% endfor %}</div>{% endif %}
  {% if not rows %}<div class="pc-empty">{{ tr('documents_none') }}</div>{% endif %}</div>""", 290, data="Documents")

sec("PCPB Contact and Map", "Live data", "Address, phone, opening hours, the map and the offices, from Settings > Contact.", "pin", TITLE + [
    f("show_map", "Check", "Show the map", default="1"), f("show_offices", "Check", "List the offices", default="1"),
    f("button_label", "Data", "Button label (e.g. Send us a message)"), f("button_url", "Data", "Button address"),
], """
{% set s = site() %}
<div class="pc-wrap pc-pad">""" + HEAD.replace("{% if view_all_url %}", "{% if false %}") + """
  <div class="pc-contact"{% if not (show_map and s.map_lat and s.map_lng) %} style="grid-template-columns:1fr"{% endif %}>
    <div class="pc-card"><dl class="pc-dl">
      {% if s.address %}<dt>{{ icon('pin') }}</dt><dd>{{ s.address | e | replace('\\n', '<br>') | safe }}</dd>{% endif %}
      {% if s.phone %}<dt>{{ icon('phone') }}</dt><dd><a href="tel:{{ s.phone | replace(' ', '') }}">{{ s.phone }}</a></dd>{% endif %}
      {% if s.email %}<dt>{{ icon('mail') }}</dt><dd><a href="mailto:{{ s.email }}">{{ s.email }}</a></dd>{% endif %}
      {% if s.hours %}<dt>{{ icon('clock') }}</dt><dd>{{ s.hours }}</dd>{% endif %}</dl>
      {% if button_label %}<div class="pc-btn-row"><a class="pc-btn primary" href="{{ lurl(button_url) }}">{{ button_label }}</a></div>{% endif %}</div>
    {% if show_map and s.map_lat and s.map_lng %}{% set la = s.map_lat | float %}{% set lo = s.map_lng | float %}
    <div class="pc-map"><iframe title="{{ tr('map') }}" loading="lazy" src="https://www.openstreetmap.org/export/embed.html?bbox={{ lo - 0.01 }}%2C{{ la - 0.006 }}%2C{{ lo + 0.01 }}%2C{{ la + 0.006 }}&amp;layer=mapnik&amp;marker={{ la }}%2C{{ lo }}"></iframe></div>{% endif %}
  </div>
  {% set offs = offices() %}{% if show_offices and offs %}<h3 style="margin-top:1.6em">{{ tr('offices') }}</h3><div class="pc-grid">{% for o in offs %}<div class="pc-card"><h3>{{ o.name }}</h3>
    {% if o.address %}<p>{{ o.address }}</p>{% endif %}{% if o.phone %}<p>{{ icon('phone') }} {{ o.phone }}</p>{% endif %}{% if o.email %}<p>{{ icon('mail') }} {{ o.email }}</p>{% endif %}</div>{% endfor %}</div>{% endif %}
</div>""", 300, data="Settings > Contact")

sec("PCPB Form", "Live data", "A web form (built in Desk > Web Form). What visitors submit lands in the ERP record the form writes to.", "form", TITLE + [
    f("web_form", "Link", "Web form", "Web Form"), f("display", "Select", "Show as", "Button\nOn the page", "Button"),
    f("button_label", "Data", "Button label"), f("height", "Int", "Height when on the page (px)", default="760"),
], """
<div class="pc-wrap pc-pad{{ '' if display == 'On the page' else ' pc-narrow pc-center' }}">{% if title %}<h2>{{ title }}</h2>{% endif %}{% if subtitle %}<p class="pc-muted">{{ subtitle }}</p>{% endif %}
  {% set route = frappe.db.get_value('Web Form', web_form, 'route') if web_form else None %}
  {% if route %}{% if display == 'On the page' %}<iframe class="pc-embed" style="min-height:{{ height or 760 }}px" src="/{{ route }}/new" title="{{ title or web_form }}" loading="lazy"></iframe>
    {% else %}<a class="pc-btn primary" href="/{{ route }}/new">{{ button_label or title or web_form }} {{ icon('arrow') }}</a>{% endif %}
  {% else %}<div class="pc-empty">{{ tr('form_pick') }}</div>{% endif %}</div>""", 310, data="Web Forms")


def scrub(n): return n.lower().replace(" ", "_")


# Frappe reloads a standard record on migrate only when the file's "modified" is newer than the site's copy, so a
# section whose fields change must get a new timestamp, and one that did not change must keep its old one.
OLD = {}
if os.path.isdir(OUT):
    for d in os.listdir(OUT):
        f = os.path.join(OUT, d, d + ".json")
        if os.path.exists(f):
            OLD[d] = json.load(open(f))
    shutil.rmtree(OUT)
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
os.makedirs(OUT)
open(os.path.join(OUT, "__init__.py"), "w").close()
cat = {}
for i, s in enumerate(S):
    folder = os.path.join(OUT, scrub(s["name"])); os.makedirs(folder)
    open(os.path.join(folder, "__init__.py"), "w").close()
    doc = {"creation": "2026-11-11 10:00:00", "docstatus": 0, "doctype": "Web Template", "fields": s["fields"], "idx": 0,
           "modified": "2026-11-11 12:00:00", "modified_by": "Administrator", "module": "PCPB Website", "name": s["name"],
           "owner": "Administrator", "standard": 1, "template": "", "type": "Section"}
    old = OLD.get(scrub(s["name"]))
    if old:
        doc["modified"] = NOW if {**old, "modified": ""} != {**doc, "modified": ""} else old["modified"]
    json.dump(doc, open(os.path.join(folder, scrub(s["name"]) + ".json"), "w"), indent=1)
    open(os.path.join(folder, scrub(s["name"]) + ".html"), "w").write(s["html"])
    cat[s["name"]] = {"label": s["name"].replace("PCPB ", ""), "category": s["category"], "description": s["description"], "icon": s["icon"],
                      "order": s["order"], "data": s["data"]}
json.dump(cat, open(os.path.join(APP, "sections.json"), "w"), indent=1)
print(len(S), "sections written")
