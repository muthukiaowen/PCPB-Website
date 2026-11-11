"""Small inline icon set used by sections, so no icon font or outside service is needed."""
from markupsafe import Markup

P = {
    "leaf": '<path d="M5 19c0-9 5-14 14-14 0 9-5 14-14 14z"/><path d="M5 19c4-5 7-8 11-11"/>',
    "sprout": '<path d="M12 20v-8"/><path d="M12 12c0-4-3-6-7-6 0 4 3 6 7 6z"/><path d="M12 14c0-3 2-5 6-5 0 3-2 5-6 5z"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "flask": '<path d="M9 3h6M10 3v6l-5 9a2 2 0 002 3h10a2 2 0 002-3l-5-9V3"/><path d="M7.5 15h9"/>',
    "alert": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "grid": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    "limit": '<circle cx="12" cy="12" r="9"/><path d="M8 12h8"/>',
    "ban": '<circle cx="12" cy="12" r="9"/><path d="M5.6 5.6l12.8 12.8"/>',
    "doc": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
    "building": '<path d="M4 21V5l8-2v18M12 9h8v12M8 8h.01M8 12h.01M8 16h.01M16 13h.01M16 17h.01M2 21h20"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2 20c0-4 3-6 7-6s7 2 7 6"/><path d="M16 5a3.5 3.5 0 010 7M18 14c2.5.6 4 2.5 4 6"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 012-2h2a2 2 0 012 2v2M3 13h18"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "pin": '<path d="M12 21s7-6.2 7-11a7 7 0 10-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "download": '<path d="M12 4v11M7 11l5 5 5-5M5 20h14"/>',
    "megaphone": '<path d="M3 10v4l11 5V5z"/><path d="M14 9a4 4 0 010 6M6 15v4h3v-3"/>',
    "gavel": '<path d="M14 4l6 6M11 7l6 6M12.5 5.5l-5 5M18.5 11.5l-5 5M9 13l-6 6 2 2 6-6"/>',
    "scale": '<path d="M12 4v16M6 20h12M5 7h14M5 7l-3 7a3 3 0 006 0zM19 7l-3 7a3 3 0 006 0z"/>',
    "book": '<path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2z"/><path d="M4 19V5M8 7h7"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
    "form": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h4"/>',
    "image": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9.5" r="1.5"/><path d="M21 16l-5-5-8 8"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    "square": '<rect x="4" y="4" width="16" height="16" rx="2"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "moon": '<path d="M20 14A8 8 0 019.5 4a8 8 0 1010.5 10z"/>',
    "up": '<path d="M6 15l6-6 6 6"/>',
    "caret": '<path d="M6 9l6 6 6-6"/>',
    "external": '<path d="M14 4h6v6M20 4l-9 9M18 13v6H5V6h6"/>',
}
NAMES = sorted(P)


def icon(name, cls=""):
    body = P.get((name or "").strip().lower()) or P["square"]
    return Markup(f'<svg class="pc-ic {cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
                  f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')
