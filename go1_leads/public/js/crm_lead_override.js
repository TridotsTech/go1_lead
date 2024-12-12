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
    console.log(data)
    const wrapper = frm.fields_dict.custom_fb_field.$wrapper
    $('[data-fieldname="custom_section_break_fqfqo"] div[class="section-head"]').remove()
    $('[data-fieldname="custom_section_break_fqfqo"]').prepend(`<div class="section-head">Facebook Lead Info</div>`)
    $('[data-fieldname="custom_fb_field"]').attr("style","display: flex;width: 100%;flex-wrap: wrap;")
    $('[data-fieldname="__column_4"]').attr("style","padding:0px !important")
    for (let i of data[0].field_data) {
        if (i.values[0].length > 140) {
            type = "Small Text"
        }
        frappe.ui.form.make_control({
            parent: wrapper,
            df: {
                "fieldtype": type,
                "label": __(`${i.name}`),
                "fieldname": `${i.name}`
            },
            render_input: true
        })
        $(`div[data-fieldname="${i.name}"]`).addClass('col-sm-4')
        $(`[data-fieldname="${i.name}"] [data-fieldname="${i.name}`).prop("value",i.values[0])
    }
}