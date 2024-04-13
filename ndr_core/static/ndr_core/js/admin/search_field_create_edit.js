// 1.) Select the type of Search Field you want to create.
let info_text_title = $('#id_info_text_title');
let info_text = $('#id_info_text_text');
let info_text_detail = $('#id_info_text_detail');
let field_type = $('#id_field_type');

// 2.) Choose a name and connect to API.
let field_name = $('#id_field_name');
let api_parameter = $('#id_api_parameter');

// 3.) Enter the text your users can see.
let field_label = $('#id_field_label');
let initial_value = $('#id_initial_value');
let field_required = $('#id_field_required');
let help_text = $('#id_help_text');

// 4.) Additional options for specific field types.
let div_list_choices = $('#div_id_list_choices');
let list_condition = $('#id_list_condition');
let lower_value = $('#id_lower_value');
let upper_value = $('#id_upper_value');

let div_text_choices = $('#div_id_text_choices');
let text_choices = $('#id_text_choices');

// 5.) Additional options for
let data_field_type = $('#id_data_field_type');
let input_transformation_regex = $('#id_input_transformation_regex');
let use_in_csv_export = $('#id_use_in_csv_export');

function setTextBox(select_value) {
    switch (select_value) {
        case '1':       // String
            info_text_title.text('String');
            info_text.text("Generates a text input field.")
            info_text_detail.html("<ul>" +
                                  "  <li>Search for text</li>" +
                                  "  <li>Use regular expressions</li>" +
                                  "  <li>Valid initial values: any text</li>" +
                                  "</ul>");
            break;
        case '2':       // Number
            info_text_title.text('Number');
            info_text.text("Generates a Number input field.")
            info_text_detail.html("<ul>" +
                                  "  <li>Search for numbers</li>" +
                                  "  <li>Define a lower and upper bound</li>" +
                                  "  <li>Valid initial values: any integer number</li>" +
                                  "</ul>");
            break;
        case '3':       // Dropdown List
            info_text_title.text('Dropdown List');
            info_text.text("Generates a dropdown list.")
            info_text_detail.html("<ul>" +
                                  "  <li>Lets you select <b>one</b> option.</li>" +
                                  "  <li>Add options below</li>" +
                                  "  <li>Options are translatable</li>" +
                                  "  <li>Valid initial values: any option <b>key</b></li>" +
                                  "</ul>");
            break;
        case '4':       // Multi Select List
            info_text_title.text('Multi Select List');
            info_text.text("Generates a dropdown list.")
            info_text_detail.html("<ul>" +
                                  "  <li>Lets you select <b>multiple</b> options.</li>" +
                                  "  <li>Add options below</li>" +
                                  "  <li>Options are translatable</li>" +
                                  "  <li>Valid initial values: any option <b>keys</b>, separated by ','</li>" +
                                  "</ul>");
            break;
        case '5':       // Boolean
            info_text_title.text('Boolean');
            info_text.text("Generates a True/False switch.")
            info_text_detail.html("<ul>" +
                                  "  <li>Search for <b>True</b> or <b>False</b>.</li>" +
                                  "  <li>Valid initial values: <b>true</b> or <b>false</b></li>" +
                                  "  <li>Field Type setting returns 'true'/'false' (string) or 0/1 (int)</li>" +
                                  "</ul>");
            break;
        case '6':       // Date
            info_text_title.text('Date');
            info_text.text("Generates a date input field.")
            info_text_detail.html("<ul>" +
                                  "  <li>Search for dates</li>" +
                                  "  <li>Define a lower and upper bound</li>" +
                                  "  <li>Valid initial values: any date (within range) in the format 'YYYY-MM-DD'</li>" +
                                  "</ul>");
            break;
        case '7':       // Date Range
            info_text_title.text('Date Range');
            info_text.text("Generates two date input fields.")
            info_text_detail.html("<ul>" +
                                  "  <li>Search for date ranges</li>" +
                                  "</ul>");
            break;
        case '8':       // Number Range
            info_text_title.text('Number Range');
            info_text.text("Generates two number input fields.")
            info_text_detail.html("<ul>" +
                                  "  <li>Search for number ranges</li>" +
                                  "  <li>Define a lower and upper bound</li>" +
                                  "  <li>Input format: 1-5,7,9,11-13</li>" +
                                  "</ul>");
            break;
        case '9':       // Hidden
            info_text_title.text('Hidden');
            info_text.text("Generates a hidden input field.")
            info_text_detail.html("<ul>" +
                                  "  <li>Field is hidden from the user.</li>" +
                                  "  <li>Can be used to pass information to the API.</li>" +
                                  "  <li>Initial value is thge passed field value.</li>" +
                                  "</ul>");
            break;
        case '10':      // Info Text
            info_text_title.text('Info Text');
            info_text.text("Generates an Info box.")
            info_text_detail.html("<ul>" +
                                  "  <li>Displays information.</li>" +
                                  "  <li>Is translatable.</li>" +
                                  "  <li>Valid initial values: any text, HTML allowed</li>" +
                                  "</ul>");
            break;
        case '11':      // Boolean List
            info_text_title.text('Boolean List');
            info_text.text("Generates a list of True/False switches.")
            info_text_detail.html("<ul>" +
                                  "  <li>Search for multiple booleans.</li>" +
                                  "  <li>Add options below</li>" +
                                  "</ul>");
            break;
        default:
            info_text_title.text('Select a Field Type');
            info_text.text("Select a field type to see more information.")
            info_text_detail.html("");
            break;
    }
}

function selectType(select_value) {
    // Set the text box
    setTextBox(select_value);

    // Set default values, valid for most field types
    field_name.removeAttr('disabled');
    api_parameter.removeAttr('disabled');
    field_label.removeAttr('disabled');
    initial_value.removeAttr('disabled');
    field_required.removeAttr('disabled');
    help_text.removeAttr('disabled');

    lower_value.attr('disabled', 'disabled');
    upper_value.attr('disabled', 'disabled');
    div_list_choices.hide();
    list_condition.attr('disabled', 'disabled');

    text_choices.attr('disabled', 'disabled');
    div_text_choices.hide();

    data_field_type.removeAttr('disabled')
    input_transformation_regex.removeAttr('disabled')
    use_in_csv_export.removeAttr('disabled')

    switch (select_value) {
        case '1':       // String
            data_field_type.attr('disabled', 'disabled');
            input_transformation_regex.attr('disabled', 'disabled');
            break;
        case '2':       // Number
            lower_value.removeAttr('disabled');
            upper_value.removeAttr('disabled');
            break;
        case '3':       // Dropdown List
            div_list_choices.show();
            data_field_type.attr('disabled', 'disabled');
            input_transformation_regex.attr('disabled', 'disabled');
            break;
        case '4':       // Multi Select List
            div_list_choices.show();
            list_condition.removeAttr('disabled');
            data_field_type.attr('disabled', 'disabled');
            input_transformation_regex.attr('disabled', 'disabled');
            break;
        case '5':       // Boolean
            field_required.attr('disabled', 'disabled');
            input_transformation_regex.attr('disabled', 'disabled');
            break;
        case '6':       // Date
            data_field_type.attr('disabled', 'disabled');
            input_transformation_regex.attr('disabled', 'disabled');
            break;
        case '7':       // Date Range
            data_field_type.attr('disabled', 'disabled');
            input_transformation_regex.attr('disabled', 'disabled');
            break;
        case '8':       // Number Range
            lower_value.removeAttr('disabled');
            upper_value.removeAttr('disabled');
            break;
        case '9':       // Hidden
            field_label.attr('disabled', 'disabled');
            field_required.attr('disabled', 'disabled');
            help_text.attr('disabled', 'disabled');
            input_transformation_regex.attr('disabled', 'disabled');
            break;
        case '10':      // Info Text
            api_parameter.attr('disabled', 'disabled');
            initial_value.attr('disabled', 'disabled');
            help_text.attr('disabled', 'disabled');
            data_field_type.attr('disabled', 'disabled');
            use_in_csv_export.attr('disabled', 'disabled');
            input_transformation_regex.attr('disabled', 'disabled');

            text_choices.removeAttr('disabled');
            div_text_choices.show();
            break;
        case '11':      // Boolean List
            div_list_choices.show();
            list_condition.removeAttr('disabled');
            data_field_type.attr('disabled', 'disabled');
            input_transformation_regex.attr('disabled', 'disabled');
            break;
        default:
            field_name.attr('disabled', 'disabled');
            api_parameter.attr('disabled', 'disabled');
            field_label.attr('disabled', 'disabled');
            initial_value.attr('disabled', 'disabled');
            field_required.attr('disabled', 'disabled');
            help_text.attr('disabled', 'disabled');
            div_list_choices.hide();
            list_condition.attr('disabled', 'disabled');
            lower_value.attr('disabled', 'disabled');
            upper_value.attr('disabled', 'disabled');
            data_field_type.attr('disabled', 'disabled');
            input_transformation_regex.attr('disabled', 'disabled');
            use_in_csv_export.attr('disabled', 'disabled');
            break;
    }


}

$(document).ready(function() {
    let list_choice_table = Tabulator.findTable("#list_choices-table")[0];
    field_type.change(function() {
        selectType(this.value)
        $.ajax({
            url: "/ndr_core/configure/search/ajax/field/"+this.value+"/header/",
            success: function(result) {
                list_choice_table.setColumns(result);
            },
            error: function(result) {
                console.log(result);
            },
            dataType: 'json'
        });
    });
    selectType(field_type.val());
});
