
function setComponents(select_value) {
    let expression = $('#div_id_expression');
    let rich_expression = $('#div_id_rich_expression');
    let field_filter = $('#div_id_field_filter');
    let field_filter_box = $('#filter_info_box');
    let info_text = $('#page_type_info')
    let display_border = $('#div_id_display_border');
    let html_display = $('#div_id_html_display');
    let md_display = $('#div_id_md_display');

    switch (select_value) {
            case '1':   // String
                expression.show();
                rich_expression.hide();
                field_filter.show();
                field_filter_box.show();
                info_text.text('Access your data by using the field name like so: {field_name} and {nested.field.name}. ' +
                               'You can apply filters to your value. You can render your expression as HTML or markdown.')
                display_border.show();
                html_display.show();
                md_display.show();
                break;
            case '2':   // Rich String
                expression.hide();
                rich_expression.show();
                field_filter.hide();
                field_filter_box.hide();
                info_text.text('You can mix and style your data by using the field name like so: {field_name} and ' +
                               '{nested.field.name}.')
                display_border.show();
                html_display.hide()
                md_display.hide()
                break;
            case '3':   // Image
                expression.show();
                rich_expression.hide();
                field_filter.hide();
                field_filter_box.hide();
                info_text.text('Provide your image url by using the field name like so: {field_name}. The content ' +
                               'of the field should be a valid url. Can also be static.')
                display_border.show();
                html_display.hide()
                md_display.hide()
                break;
            case '4':   // IIIF Image
                expression.show();
                rich_expression.show();
                field_filter.show();
                field_filter_box.show();
                info_text.text('Provide your image url by using the field name like so: {field_name}. You can apply ' +
                               'filters to your value. The content of the field should be a valid url. ' +
                               'Can also be static.')
                display_border.show();
                html_display.hide()
                md_display.hide()
                break;
            case '5':   // Table
                expression.show();
                rich_expression.hide();
                field_filter.hide();
                field_filter_box.hide();
                info_text.text('Provide an array of objects. Each object should have the same keys. ')
                display_border.show();
                html_display.show()
                md_display.show()
                break;
            case '6':   // Map
                expression.show();
                rich_expression.show();
                field_filter.show();
                field_filter_box.show();
                display_border.show();
                html_display.hide()
                md_display.hide()
                info_text.text('Not implemented yet')
                break;
        }
}
$(document).ready(function() {
    setComponents($('#id_field_type').val())
    $('#id_field_type').change(function() {
        setComponents(this.value)
    });
});
