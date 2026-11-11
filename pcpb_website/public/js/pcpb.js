/* PCPB website behaviour. No outside libraries. PCPB.init(el) wires up whatever sections are inside el. */
(function () {
  "use strict";
  var API = "/api/method/pcpb_website.api.";
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(s) { var e = document.createElement("div"); e.textContent = s == null ? "" : s; return e.innerHTML; }
  function get(method, params) {
    var u = new URLSearchParams();
    Object.keys(params || {}).forEach(function (k) { if (params[k] !== undefined && params[k] !== null && params[k] !== "") u.set(k, params[k]); });
    return fetch(API + method + "?" + u.toString(), { headers: { Accept: "application/json" } })
      .then(function (r) { return r.ok ? r.json() : {}; }).then(function (j) { return j.message; });
  }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; } }

  /* ---------- header, footer ---------- */
  function chrome() {
    document.addEventListener("click", function (ev) {
      var t = ev.target.closest ? ev.target : ev.target.parentNode;
      var b;
      if ((b = t.closest("[data-pc-burger]"))) { var n = $("#pc-nav"); b.setAttribute("aria-expanded", n.classList.toggle("open")); return; }
      if ((b = t.closest("[data-pc-sub]"))) { var it = b.parentNode, open = it.classList.toggle("open"); b.setAttribute("aria-expanded", open); $$(".pc-nav-item.open").forEach(function (o) { if (o !== it) o.classList.remove("open"); }); return; }
      if (!t.closest(".pc-nav-item")) $$(".pc-nav-item.open").forEach(function (o) { o.classList.remove("open"); });
      if ((b = t.closest("[data-pc-zoom]"))) { var z = Math.max(85, Math.min(130, (parseInt(store("pc-zoom") || "100", 10)) + 7.5 * parseInt(b.dataset.pcZoom, 10))); document.documentElement.style.fontSize = z + "%"; store("pc-zoom", z); return; }
      if ((b = t.closest("[data-pc-dark]"))) { var d = document.documentElement.getAttribute("data-pc-theme") === "dark" ? null : "dark"; if (d) document.documentElement.setAttribute("data-pc-theme", d); else document.documentElement.removeAttribute("data-pc-theme"); store("pc-theme", d); return; }
      if ((b = t.closest("[data-pc-pause]"))) { b.closest(".pc-ticker").classList.toggle("paused"); return; }
      if ((b = t.closest("[data-pc-top]"))) { window.scrollTo({ top: 0, behavior: "smooth" }); return; }
      if ((b = t.closest("a[data-pc-leave]"))) {
        var dlg = $("#pc-leave"); if (!dlg || !dlg.showModal) return;
        ev.preventDefault();
        $("#pc-leave-t").textContent = b.dataset.ext === "1" ? dlg.dataset.tExt : dlg.dataset.tPortal;
        $("#pc-leave-b").textContent = dlg.dataset.tBody + " " + (b.dataset.sys || "") + " (" + (b.dataset.svc || "") + ").";
        $("#pc-leave-go").href = b.href; dlg.showModal(); return;
      }
      if (t.closest("[data-pc-stay]")) { $("#pc-leave").close(); return; }
    });
    var top = $("[data-pc-top]");
    if (top) window.addEventListener("scroll", function () { top.classList.toggle("show", window.scrollY > 600); }, { passive: true });
    var here = location.pathname.replace(/\/$/, "") || "/";
    $$(".pc-nav a").forEach(function (a) { var p = (a.getAttribute("href") || "").split("?")[0].replace(/\/$/, "") || "/"; if (p === here) { a.classList.add("active"); var par = a.closest(".pc-nav-item"); if (par) { var l = $(".pc-nav-link", par); if (l) l.classList.add("active"); } } });
  }

  /* ---------- translation (Google Translate, loaded only when a visitor asks for it) ---------- */
  function cookie(name) { var m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)")); return m ? decodeURIComponent(m[1]) : ""; }
  function setTrans(code) {
    var host = location.hostname, parts = host.split("."), domains = ["", host];
    if (parts.length > 2) domains.push("." + parts.slice(-2).join("."), "." + parts.slice(-3).join("."));
    domains.forEach(function (d) {
      var base = "googtrans=" + (code ? "/en/" + code : "") + ";path=/" + (d ? ";domain=" + d : "");
      document.cookie = base + (code ? "" : ";expires=Thu, 01 Jan 1970 00:00:00 GMT");
    });
  }
  function translate() {
    var box = $("[data-pc-translate]"); if (!box) return;
    var menu = $(".pc-tr-menu", box), open = $("[data-pc-tr-open]", box), label = $("[data-pc-tr-label]", box);
    var current = (cookie("googtrans").split("/")[2] || "");
    var codes = $$("[data-pc-tr]", box).map(function (b) { if (b.dataset.pcTr === current && current) { label.textContent = b.textContent; b.classList.add("on"); } return b.dataset.pcTr; }).filter(Boolean);
    open.addEventListener("click", function () { menu.hidden = !menu.hidden; open.setAttribute("aria-expanded", !menu.hidden); });
    document.addEventListener("click", function (ev) { if (!box.contains(ev.target)) { menu.hidden = true; open.setAttribute("aria-expanded", "false"); } });
    box.addEventListener("click", function (ev) { var b = ev.target.closest("[data-pc-tr]"); if (!b) return; setTrans(b.dataset.pcTr); location.reload(); });
    if (current && current !== "en" && codes.indexOf(current) > -1) {
      window.pcTranslateInit = function () { new google.translate.TranslateElement({ pageLanguage: "en", includedLanguages: codes.join(","), autoDisplay: false }, "google_translate_element"); };
      var s = document.createElement("script"); s.src = "https://translate.google.com/translate_a/element.js?cb=pcTranslateInit"; s.async = true;
      s.onerror = function () { label.textContent = label.textContent + " (unavailable)"; };
      document.head.appendChild(s);
    }
  }

  /* ---------- sections ---------- */
  function slider(el) {
    var slides = $$(".pc-slide", el), dots = $$(".pc-dots button", el), i = 0, timer;
    if (slides.length < 2) return;
    function show(n) { i = (n + slides.length) % slides.length; slides.forEach(function (s, k) { s.classList.toggle("on", k === i); }); dots.forEach(function (d, k) { d.classList.toggle("on", k === i); }); }
    function play() { stop(); if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return; timer = setInterval(function () { show(i + 1); }, Math.max(2, parseInt(el.dataset.pcSlider || "6", 10)) * 1000); }
    function stop() { clearInterval(timer); }
    var p = $(".prev", el), n = $(".next", el);
    if (p) p.onclick = function () { show(i - 1); play(); };
    if (n) n.onclick = function () { show(i + 1); play(); };
    dots.forEach(function (d, k) { d.onclick = function () { show(k); play(); }; });
    el.addEventListener("mouseenter", stop); el.addEventListener("mouseleave", play);
    play();
  }
  function carousel(track) {
    var wrap = document.createElement("div"); wrap.className = "pc-carousel"; track.parentNode.insertBefore(wrap, track); wrap.appendChild(track);
    function mk(cls, label, sym) { var b = document.createElement("button"); b.type = "button"; b.className = "pc-car-btn " + cls; b.setAttribute("aria-label", label); b.innerHTML = sym; wrap.appendChild(b); return b; }
    var prev = mk("prev", "Previous", "&lsaquo;"), next = mk("next", "Next", "&rsaquo;"), timer;
    function step() { var c = track.firstElementChild; return c ? c.getBoundingClientRect().width + 18 : track.clientWidth; }
    function sync() { var max = track.scrollWidth - track.clientWidth - 2; prev.disabled = track.scrollLeft <= 2; next.disabled = track.scrollLeft >= max; var none = max <= 0; prev.hidden = next.hidden = none; }
    prev.onclick = function () { track.scrollBy({ left: -step(), behavior: "smooth" }); };
    next.onclick = function () { track.scrollBy({ left: step(), behavior: "smooth" }); };
    track.addEventListener("scroll", sync, { passive: true }); window.addEventListener("resize", sync); sync();
    var secs = parseInt(track.dataset.pcCarousel || "0", 10);
    if (secs && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      var play = function () { clearInterval(timer); timer = setInterval(function () { if (track.scrollLeft >= track.scrollWidth - track.clientWidth - 2) track.scrollTo({ left: 0, behavior: "smooth" }); else track.scrollBy({ left: step(), behavior: "smooth" }); }, secs * 1000); };
      wrap.addEventListener("mouseenter", function () { clearInterval(timer); }); wrap.addEventListener("mouseleave", play); wrap.addEventListener("focusin", function () { clearInterval(timer); }); play();
    }
  }
  function tabs(el) {
    var btns = $$(".pc-tab", el), panels = $$("[role=tabpanel]", el);
    btns.forEach(function (b, k) { b.onclick = function () { btns.forEach(function (x, j) { x.setAttribute("aria-selected", j === k ? "true" : "false"); }); panels.forEach(function (p, j) { p.hidden = j !== k; }); }; });
  }
  function gallery(el) {
    el.addEventListener("click", function (ev) {
      var fig = ev.target.closest("figure"); if (!fig) return;
      var img = $("img", fig), box = document.createElement("div");
      box.className = "pc-lightbox"; box.innerHTML = '<img src="' + img.src + '" alt=""><span>' + esc(img.alt) + "</span>";
      box.onclick = function () { box.remove(); }; document.body.appendChild(box);
    });
  }
  function check(el) {
    var form = $("form", el), input = $("input[type=search]", el), out = $(".pc-hits", el), timer;
    if (!form || !out) return;
    function run() {
      var q = input.value.trim(); if (q.length < 2) { out.innerHTML = ""; return; }
      get("search_all", { q: q }).then(function (hits) {
        if (input.value.trim() !== q) return;
        if (!hits || !hits.length) { out.innerHTML = '<div class="pc-hit">' + esc(el.dataset.none) + "</div>"; return; }
        out.innerHTML = hits.slice(0, 4).map(function (h) {
          var cls = { Banned: "bad", Withdrawn: "warn", Restricted: "warn" }[h.kind] || "ok";
          return '<div class="pc-hit"><h4><span>' + esc(h.title) + '</span><span class="pc-tag ' + cls + '">' + h.total + "</span></h4><ul>" + h.rows.slice(0, 3).map(function (r) {
            var txt = h.columns.slice(0, 3).map(function (c) { return r[c.fieldname]; }).filter(Boolean).join(" · ");
            return '<li><a href="' + h.url + "/" + encodeURIComponent(r.name) + '">' + esc(txt || r.name) + "</a></li>";
          }).join("") + "</ul></div>";
        }).join("") + '<a class="pc-link" href="/search?q=' + encodeURIComponent(q) + '">' + esc(el.dataset.more) + " &rarr;</a>";
      });
    }
    input.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(run, 300); });
  }
  function register(root) {
    var d = root.dataset, reg = d.pcRegister, page = 0, size = parseInt(d.rows || "0", 10) || undefined, timer;
    var q = $(".pc-reg-q", root), thead = $("thead", root), tbody = $("tbody", root), count = $(".pc-reg-count", root);
    var prev = $(".pc-reg-prev", root), next = $(".pc-reg-next", root), fbox = $(".pc-reg-filters", root), csv = $(".pc-reg-csv", root), clear = $(".pc-reg-clear", root);
    var filters = {}, sort = "", dir = "", built = false;
    function params() { return { register: reg, q: q.value, filters: JSON.stringify(filters) }; }
    function load() {
      var p = params(); p.start = page * (size || 25); p.page_length = size; p.sort = sort; p.sort_dir = dir;
      get("list_register", p).then(function (r) {
        if (!r || !r.columns) { tbody.innerHTML = '<tr><td>' + esc(d.lNone) + "</td></tr>"; count.textContent = ""; return; }
        size = r.page_length; sort = r.sort; dir = r.sort_dir;
        thead.innerHTML = "<tr>" + r.columns.map(function (c) {
          var arrow = c.fieldname === sort ? (dir === "asc" ? " ▲" : " ▼") : "";
          return "<th>" + (c.sortable ? '<button type="button" data-sort="' + esc(c.fieldname) + '">' + esc(c.label) + arrow + "</button>" : esc(c.label)) + "</th>";
        }).join("") + "</tr>";
        tbody.innerHTML = r.rows.length ? r.rows.map(function (row) {
          var href = (r.base_url || "/registers/" + reg) + "/" + encodeURIComponent(row.name), exp = row._expired || [];
          return "<tr>" + r.columns.map(function (c, i) {
            var v = esc(row[c.fieldname]); if (exp.indexOf(c.fieldname) > -1) v += ' <span class="pc-tag bad">' + esc(d.lExpired) + "</span>";
            return "<td>" + (i === 0 ? '<a href="' + href + '">' + (v || esc(row.name)) + "</a>" : v) + "</td>";
          }).join("") + "</tr>";
        }).join("") : '<tr><td colspan="' + (r.columns.length || 1) + '">' + esc(d.lNone) + "</td></tr>";
        var from = r.total ? r.start + 1 : 0, to = Math.min(r.start + r.page_length, r.total);
        count.textContent = d.lShowing + " " + from + "–" + to + " " + d.lOf + " " + r.total;
        prev.disabled = page === 0; next.disabled = to >= r.total;
        if (csv) { csv.hidden = !r.allow_export; var u = new URLSearchParams(params()); csv.href = API + "export_csv?" + u.toString(); }
        if (!built) { built = true; (r.filterable || []).forEach(addFilter); }
      });
    }
    function addFilter(f) {
      get("filter_options", { register: reg, fieldname: f.fieldname }).then(function (vals) {
        if (!vals || !vals.length) return;
        var s = document.createElement("select"); s.className = "pc-select"; s.setAttribute("aria-label", f.label);
        s.innerHTML = '<option value="">' + esc(d.lAll) + " – " + esc(f.label) + "</option>" + vals.map(function (v) { return '<option value="' + esc(v.value) + '">' + esc(v.label) + "</option>"; }).join("");
        s.onchange = function () { filters[f.fieldname] = s.value; page = 0; load(); };
        fbox.appendChild(s);
      });
    }
    thead.addEventListener("click", function (ev) { var b = ev.target.closest("[data-sort]"); if (!b) return; if (sort === b.dataset.sort) dir = dir === "asc" ? "desc" : "asc"; else { sort = b.dataset.sort; dir = "asc"; } page = 0; load(); });
    q.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(function () { page = 0; load(); }, 300); });
    prev.onclick = function () { page--; load(); }; next.onclick = function () { page++; load(); };
    if (clear) clear.onclick = function () { q.value = ""; filters = {}; $$("select", fbox).forEach(function (s) { s.value = ""; }); page = 0; load(); };
    var pre = new URLSearchParams(location.search).get("q"); if (pre && d.compact !== "1") q.value = pre.slice(0, 80);
    load();
  }

  var WIRES = [["[data-pc-slider]", slider], ["[data-pc-tabs]", tabs], ["[data-pc-carousel]", carousel], ["[data-pc-gallery]", gallery], ["[data-pc-check]", check], ["[data-pc-register]", register]];
  function init(root) {
    WIRES.forEach(function (w) { $$(w[0], root || document).forEach(function (el) { if (el.__pc) return; el.__pc = 1; try { w[1](el); } catch (e) { if (window.console) console.error(e); } }); });
  }
  window.PCPB = { init: init, esc: esc };
  function boot() { chrome(); translate(); init(document); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
