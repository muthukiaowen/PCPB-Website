/* PCPB visual page builder. Runs only for signed-in website staff at /page-builder.
   Pages are standard Web Pages; sections are standard Web Templates. Nothing here holds content. */
(function () {
  "use strict";
  var root = document.getElementById("pb-root");
  if (!root) return;
  var API = "/api/method/pcpb_website.builder.";
  var S = { page: null, blocks: [], library: [], dirty: false, sel: -1, manager: false, targets: [], theme: {}, themeOptions: {}, pages: [] };

  /* ---------- helpers ---------- */
  function h(tag, attrs, kids) {
    var e = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === "class") e.className = v; else if (k === "text") e.textContent = v; else if (k === "html") e.innerHTML = v;
      else if (k.slice(0, 2) === "on") e.addEventListener(k.slice(2), v); else if (k === "value") e.value = v; else if (k === "checked") e.checked = !!v;
      else e.setAttribute(k, v === true ? "" : v);
    });
    (Array.isArray(kids) ? kids : kids == null ? [] : [kids]).forEach(function (c) { if (c == null) return; e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
  }
  function esc(s) { var e = document.createElement("div"); e.textContent = s == null ? "" : s; return e.innerHTML; }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function token() { return (window.frappe && frappe.csrf_token) || ""; }
  function call(method, args, post) {
    var opt = { headers: { Accept: "application/json", "X-Frappe-CSRF-Token": token() } }, url = API + method;
    if (post) { opt.method = "POST"; opt.headers["Content-Type"] = "application/json"; opt.body = JSON.stringify(args || {}); }
    else { var u = new URLSearchParams(); Object.keys(args || {}).forEach(function (k) { u.set(k, typeof args[k] === "object" ? JSON.stringify(args[k]) : args[k]); }); url += "?" + u.toString(); }
    return fetch(url, opt).then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(serverMessage(j)); return j.message; }); });
  }
  function serverMessage(j) {
    try { var m = JSON.parse(j._server_messages || "[]").map(function (x) { return JSON.parse(x).message; }).join(" "); if (m) return m.replace(/<[^>]+>/g, ""); } catch (e) { /* fall through */ }
    return j.exception || j.exc_type || "Something went wrong";
  }
  function toast(msg, bad) {
    var t = h("div", { class: "pb-toast" + (bad ? " bad" : ""), text: msg }); document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, bad ? 6000 : 2600);
  }
  function fail(e) { toast(e.message || String(e), true); }
  function upload(file) {
    var fd = new FormData(); fd.append("file", file, file.name); fd.append("is_private", "0"); fd.append("folder", "Home");
    return fetch("/api/method/upload_file", { method: "POST", headers: { Accept: "application/json", "X-Frappe-CSRF-Token": token() }, body: fd })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(serverMessage(j)); return j.message.file_url; }); });
  }
  function modal(title, body, buttons, wide) {
    var box = h("div", { class: "pb-modal" + (wide ? " wide" : "") }, [h("header", {}, [h("h3", { text: title }), h("button", { class: "pb-x", type: "button", text: "×", onclick: close })]), h("div", { class: "pb-modal-body" }, body), h("footer", {}, buttons || [])]);
    var veil = h("div", { class: "pb-veil", onmousedown: function (ev) { if (ev.target === veil) close(); } }, box);
    function close() { veil.remove(); }
    document.body.appendChild(veil);
    return { close: close, el: box };
  }
  function btn(label, cls, fn) { return h("button", { type: "button", class: "pb-btn " + (cls || ""), text: label, onclick: fn }); }
  function field(label, input, help) { return h("label", { class: "pb-field" }, [h("span", { text: label }), input, help ? h("small", { text: help }) : null]); }
  function tpl(name) { return S.library.filter(function (t) { return t.name === name; })[0]; }
  function setDirty(v) { S.dirty = v; bar(); drawOutline(); }

  /* ---------- canvas ---------- */
  var canvas = document.getElementById("pb-canvas");
  function sections() { return Array.prototype.slice.call(canvas.children).filter(function (c) { return c.hasAttribute("data-pb"); }); }
  function renderOne(i) {
    return call("render", { block: S.blocks[i], idx: i }, true).then(function (html) {
      var tmp = document.createElement("div"); tmp.innerHTML = html; var el = tmp.firstElementChild, old = sections()[i];
      if (old) canvas.replaceChild(el, old); else canvas.appendChild(el);
      dress(el, i); if (window.PCPB) PCPB.init(el);
      return el;
    });
  }
  function renderAll() {
    canvas.innerHTML = "";
    if (!S.blocks.length) { canvas.appendChild(empty()); return Promise.resolve(); }
    var p = Promise.resolve();
    S.blocks.forEach(function (b, i) { p = p.then(function () { return renderOne(i); }); });
    return p.catch(fail);
  }
  function empty() { return h("div", { class: "pb-empty", id: "pb-empty" }, [h("h2", { text: "This page has no sections yet" }), h("p", { text: "Drag a section here from the list on the left, or click one to add it." })]); }
  function reindex() { sections().forEach(function (el, i) { el.setAttribute("data-pb", i); var t = el.querySelector(":scope > .pb-tools"); if (t) t.remove(); dress(el, i); }); if (!S.blocks.length && !document.getElementById("pb-empty")) canvas.appendChild(empty()); }
  function dress(el, i) {
    el.classList.toggle("pb-sel", i === S.sel);
    var t = tpl(S.blocks[i].web_template) || { label: S.blocks[i].web_template, description: "" };
    var about = t.label + " section" + (t.description ? ": " + t.description : "") + (t.data ? " Live from: " + t.data + "." : "");
    var old = el.querySelector(":scope > .pb-name"); if (old) old.remove();
    el.appendChild(h("div", { class: "pb-name", title: about }, [h("b", { text: (i + 1) + ". " + t.label }), t.description ? h("span", { text: t.description }) : null]));
    var tools = h("div", { class: "pb-tools" }, [
      h("span", { class: "pb-grip", draggable: "true", title: "Drag to move this section. " + about, text: "⠿ Move" }),
      tool("↑", "Move up one place", function () { move(i, i - 1); }), tool("↓", "Move down one place", function () { move(i, i + 1); }),
      tool("✎ Edit", "Edit the text, pictures and options of this section", function () { select(i); }),
      tool("⧉ Duplicate", "Make a copy of this section directly below it", function () { duplicate(i); }),
      tool(S.blocks[i].shade ? "Tinted ✓" : "Tint", "Tinted background on or off", function () { S.blocks[i].shade = S.blocks[i].shade ? 0 : 1; setDirty(true); renderOne(i); }),
      tool(S.blocks[i].hide ? "Show" : "Hide", "Hide from the public without deleting", function () { S.blocks[i].hide = S.blocks[i].hide ? 0 : 1; setDirty(true); renderOne(i); }),
      tool("🗑 Remove", "Remove this section from the page", function () { if (confirm("Remove this section from the page?")) { S.blocks.splice(i, 1); if (S.sel === i) closeEditor(); S.sel = -1; sections()[i].remove(); setDirty(true); reindex(); } }),
    ]);
    el.appendChild(tools);
    tools.querySelector(".pb-grip").addEventListener("dragstart", function (ev) { ev.dataTransfer.setData("text/pb-move", String(i)); document.body.classList.add("pb-dragging"); });
    tools.querySelector(".pb-grip").addEventListener("dragend", dragEnd);
    el.ondblclick = function (ev) { if (!ev.target.closest(".pb-tools")) select(i); };
  }
  function duplicate(i) { S.blocks.splice(i + 1, 0, clone(S.blocks[i])); setDirty(true); renderAll().then(function () { select(i + 1); var el = sections()[i + 1]; if (el) el.scrollIntoView({ behavior: "smooth", block: "center" }); toast("Section duplicated. The copy is selected."); }); }
  function tool(label, title, fn) { return h("button", { type: "button", title: title, text: label, onclick: function (ev) { ev.stopPropagation(); fn(); } }); }
  function move(from, to) {
    if (to < 0 || to >= S.blocks.length || from === to) return;
    var b = S.blocks.splice(from, 1)[0]; S.blocks.splice(to, 0, b);
    var els = sections(), el = els[from]; canvas.removeChild(el);
    var ref = sections()[to] || null; canvas.insertBefore(el, ref);
    if (S.sel === from) S.sel = to; else S.sel = -1;
    setDirty(true); reindex();
  }
  function insert(name, at) {
    var t = tpl(name), vals = {};
    (t.fields || []).forEach(function (f) { if (f.default !== null && f.default !== undefined && f.default !== "" && f.fieldtype !== "Table Break") vals[f.fieldname] = f.fieldtype === "Check" || f.fieldtype === "Int" ? parseInt(f.default, 10) || 0 : f.default; });
    if (at === undefined || at > S.blocks.length) at = S.blocks.length;
    S.blocks.splice(at, 0, { web_template: name, values: vals, hide: 0, shade: 0, section_id: "", css_class: "" });
    setDirty(true);
    renderAll().then(function () { select(at); var el = sections()[at]; if (el) el.scrollIntoView({ behavior: "smooth", block: "center" }); });
  }
  /* drag and drop: from the library (new section) or a grip (move) */
  var marker = h("div", { class: "pb-drop" });
  function dropIndex(y) { var els = sections(); for (var i = 0; i < els.length; i++) { var r = els[i].getBoundingClientRect(); if (y < r.top + r.height / 2) return i; } return els.length; }
  function dragEnd() { document.body.classList.remove("pb-dragging"); marker.remove(); }
  function wireDrop() {
    canvas.addEventListener("dragover", function (ev) {
      var types = Array.prototype.slice.call(ev.dataTransfer.types || []);
      if (types.indexOf("text/pb-new") < 0 && types.indexOf("text/pb-move") < 0) return;
      ev.preventDefault(); ev.dataTransfer.dropEffect = types.indexOf("text/pb-move") > -1 ? "move" : "copy";
      var i = dropIndex(ev.clientY), els = sections();
      canvas.insertBefore(marker, els[i] || null);
    });
    canvas.addEventListener("drop", function (ev) {
      var n = ev.dataTransfer.getData("text/pb-new"), m = ev.dataTransfer.getData("text/pb-move");
      if (!n && m === "") return; ev.preventDefault(); var i = dropIndex(ev.clientY); dragEnd();
      if (n) insert(n, i); else { var from = parseInt(m, 10); move(from, i > from ? i - 1 : i); }
    });
  }

  /* ---------- library (left) ---------- */
  var lib = h("aside", { class: "pb-lib" });
  function buildLibrary() {
    lib.innerHTML = "";
    var q = h("input", { type: "search", class: "pb-input", placeholder: "Find a section…", oninput: function () { draw(q.value.toLowerCase()); } });
    var list = h("div", { class: "pb-lib-list" });
    var addBox = h("div", { class: "pb-lib-tab" }, [h("div", { class: "pb-lib-head" }, [h("small", { text: "Drag onto the page, or click to add at the end" }), q]), list]);
    var ordBox = h("div", { class: "pb-lib-tab", hidden: true }, [h("div", { class: "pb-lib-head" }, h("small", { text: "Drag a row to move that section. Click a row to edit it." })), outline]);
    var tabA = h("button", { type: "button", class: "on", text: "Add sections", onclick: function () { tabA.className = "on"; tabB.className = ""; addBox.hidden = false; ordBox.hidden = true; } });
    var tabB = h("button", { type: "button", text: "Page order", onclick: function () { tabB.className = "on"; tabA.className = ""; addBox.hidden = true; ordBox.hidden = false; drawOutline(); } });
    lib.appendChild(h("div", { class: "pb-lib-tabs" }, [tabA, tabB])); lib.appendChild(addBox); lib.appendChild(ordBox);
    function draw(term) {
      list.innerHTML = ""; var cats = {};
      S.library.forEach(function (t) { if (term && (t.label + " " + t.description).toLowerCase().indexOf(term) < 0) return; (cats[t.category] = cats[t.category] || []).push(t); });
      Object.keys(cats).forEach(function (c) {
        list.appendChild(h("h4", { text: c }));
        cats[c].forEach(function (t) {
          var it = h("div", { class: "pb-lib-item", draggable: "true", title: t.description, onclick: function () { insert(t.name); } }, [h("b", { text: t.label }), h("span", { text: t.description }), t.data ? h("em", { text: "Live from: " + t.data }) : null]);
          it.addEventListener("dragstart", function (ev) { ev.dataTransfer.setData("text/pb-new", t.name); ev.dataTransfer.effectAllowed = "copy"; document.body.classList.add("pb-dragging"); });
          it.addEventListener("dragend", dragEnd);
          list.appendChild(it);
        });
      });
    }
    draw("");
  }

  /* ---------- page order (left, second tab): short rows that are easy to drag on a long page ---------- */
  var outline = h("div", { class: "pb-outline" });
  function drawOutline() {
    outline.innerHTML = "";
    if (!S.blocks.length) { outline.appendChild(h("p", { class: "pb-help", text: "No sections yet." })); return; }
    S.blocks.forEach(function (b, i) {
      var t = tpl(b.web_template) || { label: b.web_template }, v = b.values || {};
      var name = v.title || v.eyebrow || (v.content ? String(v.content).replace(/<[^>]+>/g, " ").trim().slice(0, 40) : "");
      var row = h("div", { class: "pb-out-row" + (i === S.sel ? " on" : "") + (b.hide ? " hid" : ""), draggable: "true", onclick: function () { select(i); var el = sections()[i]; if (el) el.scrollIntoView({ behavior: "smooth", block: "start" }); } },
        [h("span", { class: "pb-grip", text: "⠿" }), h("span", {}, [h("b", { text: t.label }), name ? h("small", { text: name }) : null]),
         h("button", { type: "button", class: "pb-mini", title: "Duplicate this section", text: "⧉", onclick: function (ev) { ev.stopPropagation(); duplicate(i); } }), h("em", { text: String(i + 1) })]);
      row.title = t.label + (t.description ? ": " + t.description : "");
      row.addEventListener("dragstart", function (ev) { ev.dataTransfer.setData("text/pb-move", String(i)); row.classList.add("drag"); });
      row.addEventListener("dragend", function () { row.classList.remove("drag"); });
      row.addEventListener("dragover", function (ev) { ev.preventDefault(); ev.dataTransfer.dropEffect = "move"; var r = row.getBoundingClientRect(); row.classList.toggle("above", ev.clientY < r.top + r.height / 2); row.classList.toggle("below", ev.clientY >= r.top + r.height / 2); });
      row.addEventListener("dragleave", function () { row.classList.remove("above", "below"); });
      row.addEventListener("drop", function (ev) {
        ev.preventDefault(); var m = ev.dataTransfer.getData("text/pb-move"), n = ev.dataTransfer.getData("text/pb-new"), r = row.getBoundingClientRect(), at = ev.clientY < r.top + r.height / 2 ? i : i + 1;
        if (n) insert(n, at); else if (m !== "") { var from = parseInt(m, 10); move(from, at > from ? at - 1 : at); }
      });
      outline.appendChild(row);
    });
  }

  /* ---------- section editor (right) ---------- */
  var panel = h("aside", { class: "pb-panel", hidden: true });
  var debounce;
  function changed() { setDirty(true); clearTimeout(debounce); var i = S.sel; debounce = setTimeout(function () { if (i > -1 && S.blocks[i]) renderOne(i).catch(fail); }, 450); }
  function closeEditor() { panel.hidden = true; document.body.classList.remove("pb-has-panel"); var old = S.sel; S.sel = -1; sections().forEach(function (el, k) { el.classList.toggle("pb-sel", false); }); return old; }
  function select(i) {
    S.sel = i; drawOutline(); sections().forEach(function (el, k) { el.classList.toggle("pb-sel", k === i); });
    var b = S.blocks[i], t = tpl(b.web_template); panel.hidden = false; document.body.classList.add("pb-has-panel"); panel.innerHTML = "";
    panel.appendChild(h("header", {}, [h("div", {}, [h("strong", { text: t ? t.label : b.web_template }), h("small", { text: (t && t.description) || "" })]), h("button", { class: "pb-x", type: "button", text: "×", onclick: closeEditor })]));
    var body = h("div", { class: "pb-panel-body" }); panel.appendChild(body);
    if (!t) { body.appendChild(h("p", { text: "This section design no longer exists. Remove the section." })); return; }
    var normal = [], tables = [], cur = null;
    t.fields.forEach(function (f) { if (f.fieldtype === "Table Break") { cur = { df: f, fields: [] }; tables.push(cur); } else if (cur) cur.fields.push(f); else normal.push(f); });
    normal.forEach(function (f) { var c = control(f, b.values); if (c) body.appendChild(c); });
    tables.forEach(function (tb) { body.appendChild(repeater(tb, b)); });
    body.appendChild(h("details", { class: "pb-adv" }, [h("summary", { text: "Advanced" }),
      field("Anchor name (for links like /page#name)", h("input", { class: "pb-input", value: b.section_id || "", oninput: function (ev) { b.section_id = ev.target.value; changed(); } })),
      field("Extra CSS class (ICT)", h("input", { class: "pb-input", value: b.css_class || "", oninput: function (ev) { b.css_class = ev.target.value; changed(); } }))]));
  }
  function control(f, store) {
    var ft = f.fieldtype, key = f.fieldname, ph = "";
    if (ft === "Column Break") return null;
    if (ft === "Section Break") return h("h4", { class: "pb-sb", text: f.label || "" });
    function set(v) { store[key] = v; changed(); }
    var val = store[key], input;
    if (ft === "Check") { input = h("input", { type: "checkbox", checked: !!parseInt(val || 0, 10), onchange: function (ev) { set(ev.target.checked ? 1 : 0); } }); return h("label", { class: "pb-check" }, [input, h("span", { text: f.label })]); }
    if (ft === "Select") {
      input = h("select", { class: "pb-input", onchange: function (ev) { set(ev.target.value); } }, (f.options || "").split("\n").map(function (o) { return h("option", { value: o, text: o }); }));
      input.value = val == null ? (f.default || "") : val; return field(f.label, input);
    }
    if (ft === "Int") return field(f.label, h("input", { class: "pb-input", type: "number", value: val == null ? "" : val, oninput: function (ev) { set(ev.target.value === "" ? "" : parseInt(ev.target.value, 10)); } }));
    if (ft === "Small Text") return field(f.label, h("textarea", { class: "pb-input", rows: 3, placeholder: ph, oninput: function (ev) { set(ev.target.value); } }, val || ""));
    if (ft === "Text") return field(f.label, h("textarea", { class: "pb-input pb-code", rows: 10, placeholder: ph, spellcheck: "false", oninput: function (ev) { set(ev.target.value); } }, val || ""));
    if (ft === "Markdown Editor") return field(f.label, rich(val || "", set, ph));
    if (ft === "Attach Image") return field(f.label, image(val || "", set));
    if (ft === "Link") {
      input = h("select", { class: "pb-input", onchange: function (ev) { set(ev.target.value); } }, [h("option", { value: "", text: "— choose —" })]);
      call("link_options", { doctype: f.options }).then(function (rows) { rows.forEach(function (r) { input.appendChild(h("option", { value: r.value, text: r.label })); }); input.value = val || ""; }).catch(fail);
      return field(f.label, input, "From " + f.options + " in the ERP");
    }
    var isUrl = /url$/.test(key);
    input = h("input", { class: "pb-input", value: val || "", placeholder: ph || (isUrl ? "/page-address or https://…" : ""), list: isUrl ? "pb-targets" : null, oninput: function (ev) { set(ev.target.value); } });
    return field(f.label, input, isUrl ? "Start typing to pick a page, register or form" : null);
  }
  function image(val, set) {
    var prev = h("div", { class: "pb-img" }), file = h("input", { type: "file", accept: "image/*", hidden: true });
    function draw(v) { prev.innerHTML = ""; if (v) prev.appendChild(h("img", { src: v, alt: "" })); else prev.appendChild(h("span", { text: "Drop a picture here, or choose one" })); }
    function take(f) { if (!f) return; prev.classList.add("busy"); upload(f).then(function (url) { prev.classList.remove("busy"); draw(url); set(url); }).catch(function (e) { prev.classList.remove("busy"); fail(e); }); }
    file.onchange = function () { take(file.files[0]); };
    prev.ondragover = function (ev) { ev.preventDefault(); prev.classList.add("over"); }; prev.ondragleave = function () { prev.classList.remove("over"); };
    prev.ondrop = function (ev) { ev.preventDefault(); ev.stopPropagation(); prev.classList.remove("over"); take(ev.dataTransfer.files[0]); };
    prev.onclick = function () { file.click(); };
    draw(val);
    return h("div", {}, [prev, file, h("div", { class: "pb-row" }, [btn("Choose picture", "sm", function () { file.click(); }), btn("Remove", "sm", function () { draw(""); set(""); })])]);
  }
  function rich(val, set, ph) {
    var ed = h("div", { class: "pb-rich", contenteditable: "true", "data-ph": ph || "Write here…", html: val });
    function cmd(c, a) { ed.focus(); document.execCommand(c, false, a || null); set(ed.innerHTML); }
    var file = h("input", { type: "file", accept: "image/*", hidden: true, onchange: function () { if (file.files[0]) upload(file.files[0]).then(function (u) { cmd("insertImage", u); }).catch(fail); } });
    var tb = h("div", { class: "pb-rich-bar" }, [["B", "bold"], ["I", "italic"], ["H2", "formatBlock", "h2"], ["H3", "formatBlock", "h3"], ["¶", "formatBlock", "p"], ["• List", "insertUnorderedList"], ["1. List", "insertOrderedList"]].map(function (x) { return h("button", { type: "button", text: x[0], onmousedown: function (ev) { ev.preventDefault(); cmd(x[1], x[2]); } }); })
      .concat([h("button", { type: "button", text: "Link", onmousedown: function (ev) { ev.preventDefault(); var u = prompt("Link address (for example /downloads or https://…)"); if (u) cmd("createLink", u); } }),
        h("button", { type: "button", text: "Picture", onmousedown: function (ev) { ev.preventDefault(); file.click(); } }),
        h("button", { type: "button", text: "Clear", title: "Remove formatting", onmousedown: function (ev) { ev.preventDefault(); cmd("removeFormat"); } })]));
    ed.addEventListener("input", function () { set(ed.innerHTML === "<br>" ? "" : ed.innerHTML); });
    ed.addEventListener("paste", function (ev) { ev.preventDefault(); var t = (ev.clipboardData || window.clipboardData).getData("text/plain"); document.execCommand("insertText", false, t); });
    return h("div", { class: "pb-richwrap" }, [tb, ed, file]);
  }
  function repeater(tb, b) {
    var key = tb.df.fieldname, wrap = h("div", { class: "pb-rep" });
    if (!Array.isArray(b.values[key])) b.values[key] = [];
    function draw(open) {
      wrap.innerHTML = ""; wrap.appendChild(h("h4", { class: "pb-sb", text: tb.df.label + " (" + b.values[key].length + ")" }));
      b.values[key].forEach(function (row, r) {
        var title = row.title || row.label || row.question || row.caption || row.number || (tb.df.label + " " + (r + 1));
        var body = h("div", { class: "pb-rep-body" }); tb.fields.forEach(function (f) { var c = control(f, row); if (c) body.appendChild(c); });
        var d = h("details", { class: "pb-rep-row", open: open === r }, [h("summary", {}, [h("span", { text: (r + 1) + ". " + String(title).slice(0, 40) }),
          h("span", { class: "pb-rep-tools" }, [mini("↑", function () { swap(r, r - 1); }), mini("↓", function () { swap(r, r + 1); }), mini("⧉", function () { b.values[key].splice(r + 1, 0, clone(row)); changed(); draw(r + 1); }), mini("🗑", function () { b.values[key].splice(r, 1); changed(); draw(); })])]), body]);
        wrap.appendChild(d);
      });
      wrap.appendChild(btn("+ Add " + tb.df.label.replace(/s$/, "").toLowerCase(), "sm", function () { b.values[key].push({}); changed(); draw(b.values[key].length - 1); }));
    }
    function swap(a, c) { var L = b.values[key]; if (c < 0 || c >= L.length) return; var x = L[a]; L[a] = L[c]; L[c] = x; changed(); draw(c); }
    function mini(label, fn) { return h("button", { type: "button", text: label, onclick: function (ev) { ev.preventDefault(); ev.stopPropagation(); fn(); } }); }
    draw();
    return wrap;
  }

  /* ---------- top bar ---------- */
  var top = h("div", { class: "pb-bar" });
  function bar() {
    top.innerHTML = "";
    var p = S.page;
    top.appendChild(h("a", { class: "pb-btn ghost", href: "/page-builder", text: "← All pages", onclick: leaveCheck }));
    if (!p) { top.appendChild(h("strong", { text: "Website builder" })); return; }
    top.appendChild(h("strong", { text: p.title }));
    var wf = p.workflow, live = p.published;
    var status = S.dirty ? "Unsaved changes" : p.has_draft ? "Draft saved, not yet live" : live ? "Live" : "Not published";
    top.appendChild(h("span", { class: "pb-chip" + (S.dirty ? " warn" : p.has_draft ? " info" : live ? " ok" : ""), text: status + (wf && wf.state ? " · " + wf.state : "") }));
    top.appendChild(h("span", { class: "pb-grow" }));
    top.appendChild(h("span", { class: "pb-seg" }, [seg("Desktop", canvasWidth === "", function () { width(""); }), seg("Tablet", canvasWidth === "820px", function () { width("820px"); }), seg("Phone", canvasWidth === "400px", function () { width("400px"); })]));
    var liveMode = document.body.classList.contains("pb-preview");
    top.appendChild(h("span", { class: "pb-seg pb-mode", title: "Build: edit the page; links do not open. Live: see and use the page as a visitor would; links open in a new tab." },
      [seg("Build", !liveMode, function () { setMode(false); }), seg("Live", liveMode, function () { setMode(true); })]));
    top.appendChild(btn("Page settings", "", pageSettings));
    top.appendChild(btn("Save draft", "", save));
    var sendable = wf && (S.dirty || p.has_draft) && (wf.send_action || wf.live_states.indexOf(wf.state) > -1);
    if (sendable) top.appendChild(btn("Save and send for approval", "primary", sendForApproval));
    if (wf) wf.actions.forEach(function (a) { if ((sendable && a === wf.send_action) || (wf.back_actions || []).indexOf(a) > -1) return; top.appendChild(btn(a, /publish/i.test(a) ? "gold" : "", function () { act(a); })); });
    else if (S.manager) top.appendChild(btn("Publish", "gold", publishNow));
    if (p.has_draft && !S.dirty) top.appendChild(btn("Discard draft", "ghost", function () { if (confirm("Throw away the draft and go back to the live version?")) call("discard_draft", { page: p.name }, true).then(function (st) { load(st); return renderAll(); }).catch(fail); }));
    if (live) top.appendChild(h("a", { class: "pb-btn ghost", href: "/" + (p.is_home ? "" : p.route), target: "_blank", text: "View live ↗" }));
  }
  function seg(label, on, fn) { return h("button", { type: "button", class: on ? "on" : "", text: label, onclick: fn }); }
  var canvasWidth = "";
  function width(w) { canvasWidth = w; canvas.style.maxWidth = w; canvas.classList.toggle("pb-narrowed", !!w); bar(); }
  function leaveCheck(ev) { if (S.dirty && !confirm("You have unsaved changes. Leave without saving?")) ev.preventDefault(); else S.dirty = false; }
  function load(st) { S.page = st; S.blocks = clone(st.blocks || []); S.dirty = false; bar(); drawOutline(); }
  function payload() { return { title: S.page.title, meta_description: S.page.meta_description, blocks: S.blocks }; }
  function save(quiet) {
    return call("save_draft", { page: S.page.name, data: payload() }, true).then(function (st) { var keep = S.blocks; load(st); S.blocks = keep; if (quiet !== true) toast("Draft saved. Visitors still see the live version until it is published."); return st; }).catch(function (e) { fail(e); throw e; });
  }
  function act(action) {
    var go = function () { return call("workflow_action", { page: S.page.name, action: action }, true).then(function (st) { load(st); toast(action + ": done" + (st.has_draft ? "" : ". The page is live.")); return renderAll(); }); };
    (S.dirty ? save() : Promise.resolve()).then(go).catch(fail);
  }
  function setMode(live) { document.body.classList.toggle("pb-preview", live); closeEditor(); bar(); toast(live ? "Live mode: the page behaves as visitors see it. Links open in a new tab." : "Build mode: edit sections. Links do not open."); }
  /* One click for content staff: keep the changes and pass them to the next person in the approval workflow. */
  function sendForApproval() {
    save(true).then(function (st) {
      var w = st.workflow;
      if (w && w.send_action) return call("workflow_action", { page: S.page.name, action: w.send_action }, true).then(function (st2) { var keep = S.blocks; load(st2); S.blocks = keep; toast("Saved and sent for approval (" + st2.workflow.state + "). Visitors see it once it is published."); });
      toast("Saved. Your role cannot send this page for approval; ask a Website Manager.", true);
    }).catch(function () { /* save already reported the problem */ });
  }
  function publishNow() { (S.dirty ? save() : Promise.resolve()).then(function () { return call("publish_now", { page: S.page.name }, true); }).then(function (st) { load(st); toast("Published. The page is live."); return renderAll(); }).catch(fail); }
  function pageSettings() {
    var p = S.page, t = h("input", { class: "pb-input", value: p.title }), md = h("textarea", { class: "pb-input", rows: 3 }, p.meta_description || "");
    var route = h("input", { class: "pb-input", value: p.route || "", disabled: !S.manager }), home = h("input", { type: "checkbox", checked: p.is_home, disabled: !S.manager || p.is_home });
    var m = modal("Page settings", [field("Page title", t), field("Description for search engines", md, "One or two sentences. Shown by Google under the page title."),
      field("Address", route, S.manager ? "The old address will forward to the new one." : "Only a Website Manager can change the address."),
      h("label", { class: "pb-check" }, [home, h("span", { text: "This is the home page" })])],
    [btn("Cancel", "ghost", function () { m.close(); }), btn("Apply", "primary", function () {
      p.title = t.value.trim() || p.title; p.meta_description = md.value.trim(); setDirty(true);
      var changes = S.manager && (route.value.trim() !== (p.route || "") || (home.checked && !p.is_home));
      m.close();
      if (changes) save().then(function () { return call("save_page_settings", { page: p.name, route: route.value.trim(), make_home: home.checked ? 1 : 0 }, true); }).then(function (st) { var keep = S.blocks; load(st); S.blocks = keep; toast("Page settings saved"); }).catch(fail);
    })]);
  }

  /* ---------- home: pages, new page, theme, menu ---------- */
  function home() {
    var box = document.getElementById("pb-home"); box.innerHTML = "";
    var wrap = h("div", { class: "pc-wrap pc-pad" });
    wrap.appendChild(h("div", { class: "pc-head" }, [h("h2", { text: "Website builder" }), h("div", { class: "pb-row" }, [btn("+ New page", "primary", newPage), btn("Getting started", "", guide), S.manager ? btn("Logo and name", "", identity) : null, S.manager ? btn("Theme", "", theme) : null, S.manager ? btn("Menu, footer and addresses", "", menu) : null])]));
    var rows = S.pages.map(function (p) {
      var st = p.has_draft ? ["Draft waiting", "info"] : p.published ? ["Live", "ok"] : ["Not published", ""];
      return h("tr", {}, [h("td", {}, [h("a", { href: "/page-builder?page=" + encodeURIComponent(p.name), text: p.title }), p.is_home ? h("span", { class: "pc-tag", text: "Home page" }) : null]),
        h("td", { text: "/" + (p.route || "") }), h("td", {}, h("span", { class: "pc-tag " + st[1], text: st[0] + (p.state ? " · " + p.state : "") })), h("td", { text: p.modified }),
        h("td", {}, [h("a", { class: "pb-btn sm primary", href: "/page-builder?page=" + encodeURIComponent(p.name), text: "Edit" }), p.published ? h("a", { class: "pb-btn sm", href: "/" + (p.is_home ? "" : p.route), target: "_blank", text: "View" }) : null,
          btn("Duplicate", "sm", function () { var t = prompt("Title of the copy", p.title + " (copy)"); if (!t) return; call("duplicate_page", { page: p.name, title: t }, true).then(function (r) { location.href = "/page-builder?page=" + encodeURIComponent(r.name); }).catch(fail); })])]);
    });
    wrap.appendChild(h("div", { class: "pc-tablewrap" }, h("table", { class: "pc-table" }, [h("thead", {}, h("tr", {}, ["Page", "Address", "Status", "Last changed", ""].map(function (x) { return h("th", { text: x }); }))), h("tbody", {}, rows)])));
    wrap.appendChild(h("div", { class: "pc-head", style: "margin-top:36px" }, [h("h2", { text: "Where the content lives" }), h("p", { text: "Pages show these lists by themselves. Add or change a record and every page that uses it updates." })]));
    var places = [["News and notices", "Posts shown by News sections and the notices ticker.", "/desk/pcpb-post"], ["Tenders", "Shown by Tenders sections. Closed tenders move to the archive by themselves.", "/desk/pcpb-tender"],
      ["Job openings", "Published by HR. Shown by Jobs sections; applications go to HR.", "/desk/job-opening"], ["Leadership", "Board and management profiles with their dates in office.", "/desk/pcpb-leader"],
      ["Documents", "Files shown by Downloads sections, by category.", "/desk/pcpb-document"], ["Registers", "Each register reads an ERP record type live. Choose the fields the public may see.", "/desk/pcpb-register"],
      ["Service descriptions", "How each portal service is described on the website.", "/desk/pcpb-service-profile"], ["Forms", "Web forms. What visitors submit lands in the ERP record the form writes to.", "/desk/web-form"],
      ["Contact, offices and wording", "Address, map, offices, the ticker and every fixed word on the site.", "/desk/pcpb-website-settings"], ["Approval steps", "Who may submit, approve and publish. Change the steps here.", "/desk/workflow"]];
    wrap.appendChild(h("div", { class: "pc-grid", style: "--cols:3" }, places.map(function (x) { return h("a", { class: "pc-card", href: x[2], target: "_blank" }, [h("h3", { text: x[0] }), h("p", { text: x[1] }), h("span", { class: "pc-more", text: "Open in Desk ↗" })]); })));
    box.appendChild(wrap);
  }
  function slug(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); }
  function newPage() {
    var title = h("input", { class: "pb-input", placeholder: "For example: Public awareness" }), route = h("input", { class: "pb-input" }), touched = false, add = h("input", { type: "checkbox" });
    var preset = h("select", { class: "pb-input" }), help = h("small", {});
    title.oninput = function () { if (!touched) route.value = slug(title.value); }; route.oninput = function () { touched = true; };
    call("presets").then(function (ps) { ps.forEach(function (p) { preset.appendChild(h("option", { value: p.key, text: p.label, "data-d": p.description })); }); preset.value = "standard"; preset.onchange = function () { help.textContent = preset.selectedOptions[0].getAttribute("data-d"); }; preset.onchange(); });
    var m = modal("New page", [field("Page title", title), field("Address", route, "The page will open at /address"), field("Start from", preset), help, S.manager ? h("label", { class: "pb-check" }, [add, h("span", { text: "Add it to the main menu" })]) : null],
      [btn("Cancel", "ghost", function () { m.close(); }), btn("Create and edit", "primary", function () {
        call("create_page", { title: title.value, route: route.value, preset: preset.value, add_to_menu: add.checked ? 1 : 0 }, true).then(function (r) { location.href = "/page-builder?page=" + encodeURIComponent(r.name); }).catch(fail);
      })]);
    title.focus();
  }
  /* Getting started: the standard Module Onboarding record, shown the way the Desk shows it. */
  var PANELS = { identity: function () { identity(); }, theme: function () { theme(); }, menu: function () { menu(); } };
  function guide() {
    var box = h("div", { class: "pb-guide" }), openName = null;
    var m = modal("Getting started", box, [], true);
    m.el.classList.add("pb-guide-modal");
    function go(st) {
      var mm = /^\/page-builder\?panel=(\w+)/.exec(st.target || "");
      if (mm && PANELS[mm[1]] && !root.dataset.page) { m.close(); PANELS[mm[1]](); }
      else if (st.target === "/page-builder" && !root.dataset.page) { m.close(); var t = document.querySelector("#pb-home .pc-tablewrap"); if (t) t.scrollIntoView({ behavior: "smooth" }); }
      else if (st.target) window.open(st.target, /^\/page-builder/.test(st.target) ? "_self" : "_blank");
    }
    function mark(st, state) { call("guide_step", { step: st.name, state: state }, true).then(draw).catch(fail); }
    function draw(g) {
      var need = g.steps.filter(function (x) { return !x.optional; }), done = need.filter(function (x) { return x.done || x.skipped; }).length;
      if (!openName) { var next = g.steps.filter(function (x) { return !x.done && !x.skipped; })[0]; openName = next ? next.name : null; }
      box.innerHTML = "";
      box.appendChild(h("div", { class: "pb-guide-head" }, [h("div", {}, [h("b", { text: g.title }), h("small", { text: done + " of " + need.length + " steps done · Deployment mode: " + g.mode })]),
        h("button", { type: "button", class: "pb-linkbtn", text: "Dismiss", onclick: function () { try { localStorage.setItem("pb-guide-seen", "1"); } catch (e) { /* private browsing */ } m.close(); } })]));
      box.appendChild(h("div", { class: "pb-guide-bar" }, need.map(function (x) { return h("i", { class: x.done || x.skipped ? "on" : "" }); })));
      g.steps.forEach(function (st) {
        var open = st.name === openName, state = st.done ? "done" : st.skipped ? "skipped" : "";
        var head = h("button", { type: "button", class: "pb-gstep-head", onclick: function () { openName = open ? "-" : st.name; draw(g); } },
          [h("span", { class: "pb-gtick " + state, text: st.done ? "✓" : st.skipped ? "–" : "" }), h("span", { class: "pb-gtitle", text: st.title }), st.optional ? h("em", { text: "Optional" }) : null]);
        var kids = [head];
        if (open) {
          var acts = [btn(st.label + " →", "dark", function () { go(st); })];
          if (g.is_manager) {
            if (!st.done && !st.skipped) acts.push(btn("Skip", "sm", function () { openName = null; mark(st, "skipped"); }));
            if (!st.done) acts.push(btn("Mark as done", "sm", function () { openName = null; mark(st, "done"); }));
            else acts.push(btn("Mark as not done", "sm", function () { mark(st, "open"); }));
          }
          kids.push(h("div", { class: "pb-gstep-body" }, [h("div", { class: "pb-gdesc", html: st.description }), h("div", { class: "pb-row" }, acts)]));
        }
        box.appendChild(h("div", { class: "pb-gstep" + (open ? " open" : "") + (state ? " " + state : "") }, kids));
      });
      box.appendChild(h("p", { class: "pb-help", style: "margin-top:14px" }, ["Full reference: ", h("a", { href: g.guide, target: "_blank", text: "administrator guide" }), " · ", h("a", { href: g.readme, target: "_blank", text: "read me on GitHub" }),
        g.is_manager ? " · " : null, g.is_manager ? h("a", { href: g.edit_url, target: "_blank", text: "edit these steps" }) : null]));
      try { localStorage.setItem("pb-guide-seen", "1"); } catch (e) { /* private browsing */ }
    }
    call("getting_started").then(draw).catch(fail);
  }
  function identity() {
    call("get_identity").then(function (v) {
      function text(key, label, help) { var i = h("input", { class: "pb-input", value: v[key] || "", oninput: function () { v[key] = i.value; } }); return field(label, i, help); }
      function pic(key, label, help) { return field(label, image(v[key] || "", function (url) { v[key] = url; }), help); }
      var m = modal("Logo and name", [
        pic("logo", "Logo", "Shown in the header of every page. A PNG or SVG with a transparent background works best."),
        (function () { var i = h("input", { type: "checkbox", checked: !!parseInt(v.logo_on_desk || 0, 10), onchange: function () { v.logo_on_desk = i.checked ? 1 : 0; } }); return h("label", { class: "pb-check" }, [i, h("span", { text: "Use this logo in the Desk as well (the PCPB Website icon, the Desk logo and the sign-in page)" })]); })(),
        text("logo_alt", "Logo description", "Read out by screen readers, for example: Pest Control Products Board logo"),
        text("site_name", "Organisation name"), text("parent_body", "Parent ministry or department", "Small print under the name"), text("tagline", "Tagline"),
        pic("footer_logo", "Footer logo (optional)", "A light version for the dark footer."),
        pic("favicon", "Browser tab icon", "A small square picture, shown on the browser tab.")],
      [btn("Cancel", "ghost", function () { m.close(); }), btn("Save", "primary", function () { call("save_identity", { values: v }, true).then(function () { toast("Saved. Reloading…"); setTimeout(function () { location.reload(); }, 700); }).catch(fail); })]);
    }).catch(fail);
  }
  function theme() {
    var v = clone(S.theme), styleEl = document.getElementById("pb-theme-preview") || document.head.appendChild(h("style", { id: "pb-theme-preview" }));
    function preview() { call("preview_theme", { values: v }, true).then(function (css) { styleEl.textContent = ":root{" + css + "}"; }).catch(fail); }
    function color(key, label) { var i = h("input", { type: "color", value: v[key] || "#000000", oninput: function () { v[key] = i.value; preview(); } }); return h("label", { class: "pb-color" }, [i, h("span", { text: label })]); }
    function sel(key, label) { var s = h("select", { class: "pb-input", onchange: function () { v[key] = s.value; preview(); } }, (S.themeOptions[key] || []).map(function (o) { return h("option", { value: o, text: o }); })); s.value = v[key] || ""; return field(label, s); }
    function num(key, label, min, max) { var i = h("input", { type: "range", min: min, max: max, value: v[key] || min, oninput: function () { v[key] = parseInt(i.value, 10); out.textContent = i.value + " px"; preview(); } }), out = h("small", { text: (v[key] || min) + " px" }); return field(label, h("div", { class: "pb-row" }, [i, out])); }
    function chk(key, label) { var i = h("input", { type: "checkbox", checked: !!parseInt(v[key] || 0, 10), onchange: function () { v[key] = i.checked ? 1 : 0; } }); return h("label", { class: "pb-check" }, [i, h("span", { text: label })]); }
    var m = modal("Theme", [h("p", { class: "pb-help", text: "The theme applies to every page. Move this window aside to watch the page change as you choose." }),
      h("div", { class: "pb-colors" }, [color("color_primary", "Main colour"), color("color_dark", "Dark colour (header strip, footer)"), color("color_accent", "Accent (buttons, highlights)"), color("color_soft", "Soft tint (panels)"), color("color_bg", "Page background"), color("color_text", "Text")]),
      sel("font_body", "Body font"), sel("font_heading", "Heading font"), num("radius", "Corner roundness", 0, 30), num("page_width", "Page width", 960, 1600),
      chk("show_flag_bar", "Show the national colours strip"), chk("allow_dark_mode", "Offer a dark mode button"), chk("allow_text_size", "Offer text size buttons")],
    [btn("Cancel", "ghost", function () { styleEl.textContent = ""; m.close(); }), btn("Save theme", "primary", function () { call("save_theme", { values: v }, true).then(function () { S.theme = v; toast("Theme saved for the whole site"); m.close(); }).catch(fail); })]);
  }
  function menu() {
    call("get_menu").then(function (data) {
      function editor(rows, withParent) {
        var box = h("div", { class: "pb-menu" });
        function draw() {
          box.innerHTML = "";
          var parents = rows.filter(function (r) { return !r.parent_label; }).map(function (r) { return r.label; });
          rows.forEach(function (r, i) {
            var par = h("select", { class: "pb-input", onchange: function () { r.parent_label = par.value; } }, [h("option", { value: "", text: "(top level)" })].concat(parents.filter(function (p) { return p !== r.label; }).map(function (p) { return h("option", { value: p, text: "under " + p }); })));
            par.value = r.parent_label || "";
            var row = h("div", { class: "pb-menu-row" + (r.parent_label ? " child" : ""), draggable: "true" }, [h("span", { class: "pb-grip", text: "⠿" }),
              h("input", { class: "pb-input", value: r.label, placeholder: "Label", oninput: function (ev) { r.label = ev.target.value; } }),
              h("input", { class: "pb-input", value: r.url || "", placeholder: "Address (empty = heading only)", list: "pb-targets", oninput: function (ev) { r.url = ev.target.value; } }),
              withParent ? par : null, h("button", { type: "button", class: "pb-x", text: "×", onclick: function () { rows.splice(i, 1); draw(); } })]);
            row.addEventListener("dragstart", function (ev) { ev.dataTransfer.setData("text/pb-menu", String(i)); ev.dataTransfer.effectAllowed = "move"; });
            row.addEventListener("dragover", function (ev) { ev.preventDefault(); ev.dataTransfer.dropEffect = "move"; });
            row.addEventListener("drop", function (ev) { ev.preventDefault(); var from = parseInt(ev.dataTransfer.getData("text/pb-menu"), 10); if (isNaN(from) || from === i) return; var x = rows.splice(from, 1)[0]; rows.splice(i, 0, x); draw(); });
            box.appendChild(row);
          });
          box.appendChild(btn("+ Add item", "sm", function () { rows.push({ label: "", url: "", parent_label: "" }); draw(); }));
        }
        draw(); return box;
      }
      function redirects(rows) {
        var box = h("div", { class: "pb-menu" });
        function draw() { box.innerHTML = ""; rows.forEach(function (r, i) { box.appendChild(h("div", { class: "pb-menu-row" }, [h("input", { class: "pb-input", value: r.source, placeholder: "Short address, e.g. jobs", oninput: function (ev) { r.source = ev.target.value; } }), h("span", { text: "→" }), h("input", { class: "pb-input", value: r.target, placeholder: "Goes to, e.g. /careers", list: "pb-targets", oninput: function (ev) { r.target = ev.target.value; } }), h("button", { type: "button", class: "pb-x", text: "×", onclick: function () { rows.splice(i, 1); draw(); } })])); }); box.appendChild(btn("+ Add address", "sm", function () { rows.push({ source: "", target: "" }); draw(); })); }
        draw(); return box;
      }
      var m = modal("Menu, footer and addresses", [h("h4", { class: "pb-sb", text: "Main menu" }), h("p", { class: "pb-help", text: "Drag the rows to change the order. An item placed under another one appears in its drop-down." }), editor(data.top, true),
        h("h4", { class: "pb-sb", text: "Footer links" }), h("p", { class: "pb-help", text: "A top level item with no address is a column heading; the items under it form the column." }), editor(data.footer, true),
        h("h4", { class: "pb-sb", text: "Short addresses" }), h("p", { class: "pb-help", text: "A short or old address that should take visitors to a page. Example: jobs goes to /careers." }), redirects(data.redirects)],
      [btn("Cancel", "ghost", function () { m.close(); }), btn("Save", "primary", function () { call("save_menu", { data: data }, true).then(function () { toast("Saved. Reloading…"); setTimeout(function () { location.reload(); }, 700); }).catch(fail); })], true);
    }).catch(fail);
  }

  /* ---------- start ---------- */
  function start(st) {
    S.library = st.library; S.manager = st.is_manager; S.theme = st.theme || {}; S.themeOptions = st.theme_options || {}; S.pages = st.pages || [];
    document.body.classList.add("pb-on"); document.body.insertBefore(top, document.body.firstChild);
    call("link_targets").then(function (ts) { var dl = h("datalist", { id: "pb-targets" }, ts.map(function (t) { return h("option", { value: t.url, label: t.group + ": " + t.label }); })); document.body.appendChild(dl); }).catch(function () {});
    if (!root.dataset.page) {
      bar(); home();
      var seen = false; try { seen = !!localStorage.getItem("pb-guide-seen"); } catch (e) { seen = true; }
      var want = /[?&]panel=(\w+)/.exec(location.search);
      if (want && PANELS[want[1]] && S.manager) PANELS[want[1]]();
      else if (!seen || /[?&]guide=1/.test(location.search)) guide();
      return;
    }
    load(st.page); document.body.classList.add("pb-editing"); document.body.appendChild(lib); document.body.appendChild(panel);
    buildLibrary(); wireDrop(); reindex();
    if (!st.page.is_builder) toast("This page was written in the Desk editor. Adding sections here will replace that text when published.", true);
    window.addEventListener("beforeunload", function (ev) { if (S.dirty) { ev.preventDefault(); ev.returnValue = ""; } });
    /* Build mode: nothing on the page navigates. Live mode: links work, in a new tab, so the builder stays open. */
    var lastNote = 0;
    document.addEventListener("click", function (ev) {
      var a = ev.target.closest && ev.target.closest("a[href]");
      if (!a || a.closest(".pb-bar,.pb-lib,.pb-panel,.pb-modal,.pb-veil")) return;
      var href = a.getAttribute("href") || "";
      if (document.body.classList.contains("pb-preview")) { if (href && href.charAt(0) !== "#" && a.target !== "_blank") { ev.preventDefault(); window.open(a.href, "_blank", "noopener"); } return; }
      ev.preventDefault(); ev.stopPropagation();
      if (Date.now() - lastNote > 4000) { lastNote = Date.now(); toast("Build mode: links do not open here. Switch to Live to follow them."); }
    }, true);
    document.addEventListener("submit", function (ev) { if (!document.body.classList.contains("pb-preview") && !ev.target.closest(".pb-bar,.pb-lib,.pb-panel,.pb-modal")) ev.preventDefault(); }, true);
    document.addEventListener("keydown", function (ev) { if ((ev.ctrlKey || ev.metaKey) && ev.key === "s") { ev.preventDefault(); save(); } if (ev.key === "Escape" && !panel.hidden) closeEditor(); });
  }
  call("state", root.dataset.page ? { page: root.dataset.page } : {}).then(start).catch(fail);
})();
