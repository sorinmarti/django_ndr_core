/**
 * This function is used to get the masked url for the preview image. It replaces the string "image_string" with the
 * data_array. The data_array is a list of strings that are separated by a "~". The data_array is created by getting the
 * values from the form fields.
 *
 * The form has 20 fields for the row, column, size and search. The data_array is created by looping through the 20 fields.
 *
 * @param baseUrl - The base url for the preview image. It must contain the string "image_string"
 * @param dropdown_field_id - The id of the dropdown field. It is used to get the value of the dropdown field.
 * @param field_count - The number of fields to loop through. The default is 20.
 * @param row_field_id - The id of the row field. It is used to get the value of the row field.
 * @param column_field_id - The id of the column field. It is used to get the value of the column field.
 * @param size_field_id - The id of the size field. It is used to get the value of the size field.
 * @returns {*} - The masked url for the preview image.
 */
function getMaskedUrl(baseUrl, dropdown_field_id, field_count=20,
                      row_field_id, column_field_id, size_field_id) {

    let data_array = [];
    for (let i = 0; i < field_count; i++) {
        let row_field =  $(row_field_id + '_' +i);
        let column_field =  $(column_field_id + '_' +i);
        let size_field = $(size_field_id + '_'+i);
        let dropdown_field = $(dropdown_field_id+'_'+i);
        data_array[i]=row_field.val()+"~"+column_field.val()+"~"+size_field.val()+"~"+dropdown_field.val();
    }
    return baseUrl.replace("image_string", data_array);
}

function configureDropdown(selectElement, totalElements, updateFunc, dropdown_field_id) {

    selectElement.change(function(e) {
        let before_change = $(this).data('pre');//get the pre data
        $(this).data('pre', $(this).val());//update the pre data
        let after_change = $(this).data('pre');//get the pre data
        let this_index = this.id.split('_').slice(-1);
        if(before_change !== '') {
            for (let x = 0; x < totalElements; x++) {
                if(x !== parseInt(this_index)) {
                    $(dropdown_field_id+'_'+x+' option[value="'+before_change+'"]').removeAttr("disabled");
                }
            }
        }
        if(after_change !== '') {
            for (let x = 0; x < totalElements; x++) {
                if(x !== parseInt(this_index)) {
                    $(dropdown_field_id+'_'+x+' option[value="'+after_change+'"]').attr("disabled", "disabled");
                }
            }
        }

        // Update the image
        updateFunc();
    });
}

/**
 * This function is used to configure the rows for the form. It loops through the number of rows and configures the
 * dropdowns for each row. It also adds the change event to the row, column and size fields.
 * @param number - The number of rows to configure
 * @param imageBaseUrl - The base url for the preview image. It must contain the string "image_string"
 * @param dropdown_field_id - The id of the dropdown field. It is used to get the value of the dropdown field.
 * @param image_field_id - The id of the preview image. It is used to update the src attribute.
 * @param row_field_id - The id of the row field. It is used to get the value of the row field.
 * @param column_field_id - The id of the column field. It is used to get the value of the column field.
 * @param size_field_id - The id of the size field. It is used to get the value of the size field.
 */
function configureRows(number, imageBaseUrl, dropdown_field_id, image_field_id,
                       row_field_id, column_field_id, size_field_id) {
    /**
     * This function is used to update the preview image. It gets the masked url and updates the src attribute of the
     * preview image.
     */
    let updateFunc = function updateImage() {
        let previewImage = $(image_field_id);
        let maskedUrl = getMaskedUrl(imageBaseUrl, dropdown_field_id, 20,
                                     row_field_id, column_field_id, size_field_id);
        previewImage.attr('src', maskedUrl);
    }

    for (let i = 0; i < number; i++) {
        let selectElement = $(dropdown_field_id+'_'+i);
        configureDropdown(selectElement, number, updateFunc, dropdown_field_id);

        $(row_field_id+'_'+i).on('change', updateFunc);
        $(column_field_id+'_'+i).on('change', updateFunc);
        $(size_field_id+'_'+i).on('change', updateFunc);
    }
}

/**
 * This function is used to initialize the add and remove buttons for the form.
 * @param row_id - The id of the row. It is used to show and hide the rows.
 * @param dropdown_id - The id of the dropdown field. It is used to get the value of the dropdown field.
 * @param visible_buttons - The number of visible buttons. The default is 1.
 * @param add_button_id - The id of the add button. It is used to add a row.
 * @param remove_button_id - The id of the remove button. It is used to remove a row.
 * @param row_field_id - The id of the row field. It is used to get the value of the row field.
 * @param column_field_id - The id of the column field. It is used to get the value of the column field.
 * @param size_field_id - The id of the size field. It is used to get the value of the size field.
 */
function initializeAddAndRemoveButtons(row_id, dropdown_id, visible_buttons=1,
                                       add_button_id, remove_button_id,
                                       row_field_id, column_field_id, size_field_id) {
    let addButton = $(add_button_id);
    let removeButton = $(remove_button_id);

    addButton.on('click', function () {
        removeButton.show();
        if (visible_buttons < 19) {
            visible_buttons += 1;
            $(row_id + '_' + visible_buttons).show(); // #search_field_config_row_x
        }
        if (visible_buttons === 19) {
            addButton.hide();
        }

        //console.log(visible_buttons);
    });

    removeButton.on('click', function () {
        if(visible_buttons > 0) {
            let sField = $(dropdown_id + '_'+visible_buttons);
            sField.val(null);
            sField.change();
            $(row_field_id + '_'+visible_buttons).val("");
            $(column_field_id + '_'+visible_buttons).val("");
            $(size_field_id + '_'+visible_buttons).val("");
            $(row_id + '_'+visible_buttons).hide();

            if (visible_buttons === 1) {
                removeButton.hide();
            }
            if (visible_buttons === 19) {
                addButton.show();
            }
            visible_buttons -= 1;
        }
    });
}

function init_preview(imageBaseUrl, dropdown_field_id, image_field_id, result_field_config_row_stub,
                      row_field_id, column_field_id, size_field_id,
                      add_button_id, remove_button_id) {

    configureRows(20, imageBaseUrl, dropdown_field_id, image_field_id,
                  row_field_id, column_field_id, size_field_id);

    let visible_buttons = 1;
    for(let i = 1; i < 20; i++){
        if($(dropdown_field_id + '_' + i).val() === '') {
            $(result_field_config_row_stub + '_' + i).hide();
        }
        else {
            visible_buttons++;
        }
    }

    initializeAddAndRemoveButtons(result_field_config_row_stub, dropdown_field_id, visible_buttons,
                                  add_button_id, remove_button_id,
                                  row_field_id, column_field_id, size_field_id);

    let maskedUrl = getMaskedUrl(imageBaseUrl, dropdown_field_id, 20, row_field_id, column_field_id, size_field_id);
    let previewImage = $(image_field_id);
    previewImage.attr('src', maskedUrl);
}