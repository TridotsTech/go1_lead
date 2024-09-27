// Copyright (c) 2024, Tridots Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Go1 FB Lead Form", {

    refresh(frm) {
        if (!frm.doc.__islocal && !frm.doc.form_id) {
            frm.add_custom_button("Push Lead Form", function () {
                frappe.call({
                    method: "go1_leads.go1_leads.doctype.go1_fb_lead_form.go1_fb_lead_form.get_fb_pages",
                    args: {
                        doc: frm.doc
                    },
                    freeze: true,
                    freeze_message: "Fetching Pages",
                    async: true,
                    callback(r) {
                        if (r.message) {
                            let page_options = []
                            for (let i of r.message.message.data) {
                                page_options.push(i.name)
                            }
                            let page_popup = [
                                {
                                    'label': "Select Page",
                                    'fieldname': "page",
                                    'fieldtype': "Select",
                                    'options': page_options
                                }
                            ]
                            let d = new frappe.ui.Dialog({
                                'title': "Select Page to Publish Post",
                                'fields': page_popup,
                                'primary_action': function () {
                                    // let page = d.get_value("page")
                                    console.log(d.get_value("page"))
                                    console.log(r.message.message.data)
                                    frappe.call({
                                        method: "go1_leads.go1_leads.doctype.go1_fb_lead_form.go1_fb_lead_form.push_lead_form",
                                        args: {
                                            doc: frm.doc,
                                            page_data: r.message.message.data,
                                            selected_page: d.get_value("page")
                                        },
                                        freeze: true,
                                        freeze_message: "Publishing Form",
                                        callback(r) {
                                            if (r.message) {
                                                if (r.message.status == "success") {
                                                    frm.set_value("form_id", r.message.message.id)
                                                    frm.save()
                                                }
                                            }
                                            d.hide()
                                        }
                                    })
                                }
                            })
                            d.show()
                        }
                    }
                })
            })
        }

        if (frm.doc.form_id) {
            frm.add_custom_button("Pull Lead", function () {
                frappe.call({
                    method: "go1_leads.go1_leads.doctype.go1_fb_lead_form.go1_fb_lead_form.pull_fb_lead",
                    args: {
                        doc: frm.doc
                    },
                    freeze: true,
                    freeze_message: "Pulling leads",
                    callback(r) {
                        if (r.message) {
                            // frappe.msgprint("Leads Pulled succesfully");
                        }
                    }
                })
            })
        }
    },
});

