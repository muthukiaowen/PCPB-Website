Developer helpers. They only write files in the app; they hold no website content that staff edit.

    python3 dev/sections.py    # section library (Web Templates) and sections.json
    python3 dev/starter.py     # first-install pages, menu, redirects and page presets
    python3 -c "import sys; sys.path.insert(0,'dev'); import doctypes"   # DocType JSON
