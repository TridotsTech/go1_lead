// Copyright (c) 2024, Tridots Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lead Integration", {
	refresh(frm) {
        frm.add_custom_button("Pull Lead",()=>{
            frm.call({
                doc:frm.doc,
                method:"pull_leads",
                async:false,
                callback(r){
                    if(r.message){
                        frappe.msgprint("Leads Pulled succesfully");
                    }
                }
            })
        })
	},
});
