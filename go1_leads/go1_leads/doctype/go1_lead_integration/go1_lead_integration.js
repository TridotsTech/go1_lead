// Copyright (c) 2024, Tridots Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Go1 Lead Integration', {
	refresh(frm) {
        frm.add_custom_button("Pull Lead",()=>{
            frm.call({
                doc:frm.doc,
                method:"pull_leads",
                args:{
                    "lead_app":frm.doc.lead_app
                },
                async:true,
                freeze:true,
                freeze_message:"Pulling leads",
                callback(r){
                    if(r.message){
                        frappe.msgprint("Leads Pulled succesfully");
                    }
                }
            })
        })
	},
});
