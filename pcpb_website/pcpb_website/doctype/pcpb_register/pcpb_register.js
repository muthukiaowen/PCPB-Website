frappe.ui.form.on("PCPB Register", {
  refresh(frm) {
    if (!frm.is_new() && frm.doc.published) {
      frm.add_web_link("/" + (frm.doc.route || "registers/" + frm.doc.name), __("Open on the website"));
    }
  },
  title(frm) {
    if (frm.is_new() && !frm.doc.slug && frm.doc.title) {
      frm.set_value("slug", frm.doc.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""));
    }
  },
  add_publish_tick(frm) {
    if (frm.is_new() || frm.is_dirty()) {
      frappe.msgprint(__("Save the register first."));
      return;
    }
    frappe.confirm(__("Add a 'Publish on Website' tick box to {0} and show only ticked records on the website?", [frm.doc.source_doctype]), () => {
      frappe.call({ method: "pcpb_website.api.add_publish_tick", args: { register: frm.doc.name } }).then(() => {
        frappe.show_alert({ message: __("Done. Tick 'Publish on Website' on a {0} to show it on the website.", [frm.doc.source_doctype]), indicator: "green" });
        frm.reload_doc();
      });
    });
  },
  load_fields(frm) {
    if (frm.is_new() || frm.is_dirty()) {
      frappe.msgprint(__("Save the register first."));
      return;
    }
    frappe.call({ method: "pcpb_website.api.load_register_fields", args: { register: frm.doc.name } }).then((r) => {
      frappe.show_alert({ message: __("{0} fields listed. Tick the ones the public may see.", [r.message || 0]), indicator: "green" });
      frm.reload_doc();
    });
  },
});
