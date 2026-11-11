frappe.ui.form.on("PCPB Website Integration", {
  test_connection(frm) {
    const run = () => frappe.call({ method: "pcpb_website.remote.test_connection" }).then((r) => {
      const m = r.message || {};
      frappe.msgprint({ title: m.ok ? __("Connection successful") : __("Connection failed"), message: m.message || "", indicator: m.ok ? "green" : "red" });
      frm.reload_doc();
    });
    if (frm.is_dirty()) frm.save().then(run); else run();
  },
  create_api_user(frm) {
    frappe.confirm(__("Create the integration user (or issue new keys for it)? Any earlier secret for this user stops working."), () => {
      frappe.call({ method: "pcpb_website.pcpb_website.doctype.pcpb_website_integration.pcpb_website_integration.create_integration_user" }).then((r) => {
        const m = r.message;
        frappe.msgprint({
          title: __("Copy these to the website server"), indicator: "green",
          message: `<p>${__("Enter them in Integration Settings on the website server. The secret is shown only this once.")}</p>
            <p><b>${__("API Key")}</b><br><code>${m.api_key}</code></p><p><b>${__("API Secret")}</b><br><code>${m.api_secret}</code></p>
            <p class="text-muted">${__("User")}: ${m.user}</p>`,
        });
        frm.reload_doc();
      });
    });
  },
});
