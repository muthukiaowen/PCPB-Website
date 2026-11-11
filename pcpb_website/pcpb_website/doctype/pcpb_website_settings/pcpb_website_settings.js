frappe.ui.form.on("PCPB Website Settings", {
  refresh(frm) {
    frm.add_custom_button(__("Open the website builder"), () => window.open("/page-builder", "_blank"));
    frm.add_custom_button(__("Getting started"), () => window.open("/page-builder?guide=1", "_blank"));
  },
});
