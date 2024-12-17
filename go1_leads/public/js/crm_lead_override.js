frappe.ui.form.on("CRM Lead", {
    refresh(frm){
        frm.fields_dict.custom_fb_field.$wrapper.empty()
        $('[data-fieldname="custom_section_break_fqfqo"] div[class="section-head"]').remove()
        if(!frm.doc.__islocal){
            if(frm.doc.custom_fb_data){
                render_fields(frm)
            }
        }
    }
})
function render_fields(frm) {
    data = JSON.parse(frm.doc.custom_fb_data)
    let type = "Data"
    // console.log(data)
    const wrapper = frm.fields_dict.custom_fb_field.$wrapper
    $('[data-fieldname="custom_section_break_fqfqo"] div[class="section-head"]').remove()
    $('[data-fieldname="custom_section_break_fqfqo"]').prepend(`<div class="section-head">Facebook Lead Info</div>`)
    $('[data-fieldname="custom_fb_field"]').attr("style","display: flex;width: 100%;flex-wrap: wrap;")
    $('[data-fieldname="__column_3"]').attr("style","padding:0px !important")
    for (let i of data[0].field_data) {
        label = (i.name).split('_').map(function (word) {
            return (word.charAt(0).toUpperCase() + word.slice(1));
        }).join(' ');
        fieldname = (i.name).split(' ').join('_').toLowerCase();
        if (i.values[0].length > 140) {
            type = "Small Text"
        }
        frappe.ui.form.make_control({
            parent: wrapper,
            df: {
                "fieldtype": type,
                "label": __(`${label}`),
                "fieldname": `${fieldname}`
            },
            render_input: true
        })
        $(`div[data-fieldname="${fieldname}"]`).addClass('col-sm-4')
        $(`[data-fieldname="${fieldname}"] [data-fieldname="${fieldname}`).prop("value",i.values[0])
    }
    for(let [key,values] of Object.entries(data[0])){
        if (key != "field_data"){
            label = key.split('_').map(function (word) {
                return (word.charAt(0).toUpperCase() + word.slice(1));
            }).join(' ');
            fieldname = key.split(' ').join('_').toLowerCase();
            if (values.length > 140) {
                type = "Small Text"
            }
            frappe.ui.form.make_control({
                parent: wrapper,
                df: {
                    "fieldtype": type,
                    "label": __(`${label}`),
                    "fieldname": `${fieldname}`
                },
                render_input: true
            })
            $(`div[data-fieldname="${fieldname}"]`).addClass('col-sm-4')
            $(`[data-fieldname="${fieldname}"] [data-fieldname="${fieldname}`).prop("value",values)
        }
        // console.log(key,values)
    }
}