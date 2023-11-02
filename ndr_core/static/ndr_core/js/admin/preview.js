/**
 * This function is used to get the masked url for the preview image. It replaces the string "image_string" with the
 * data_array. The data_array is a list of strings that are separated by a "~". The data_array is created by getting the
 * values from the form fields.
 *
 * The form has 20 fields for the row, column, size and search. The data_array is created by looping through the 20 fields.
 *
 * @param baseUrl - The base url for the preview image. It must contain the string "image_string"
 * @returns {*} - The masked url for the preview image.
 */
function getMaskedUrl(baseUrl, dropdown_field_id, field_count=20){
    let data_array = [];
    for (let i = 0; i < field_count; i++) {
        let row_field =  $('#id_row_field_'+i);
        let column_field =  $('#id_column_field_'+i);
        let size_field = $('#id_size_field_'+i);
        let dropdown_field = $(dropdown_field_id+'_'+i);
        console.log(dropdown_field, dropdown_field_id+'_'+i, dropdown_field.val());
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
 */
function configureRows(number, imageBaseUrl, dropdown_field_id, image_field_id) {
    /**
     * This function is used to update the preview image. It gets the masked url and updates the src attribute of the
     * preview image.
     */
    let updateFunc = function updateImage() {
        let previewImage = $(image_field_id);
        let maskedUrl = getMaskedUrl(imageBaseUrl, dropdown_field_id);
        previewImage.attr('src', maskedUrl);
    }

    for (let i = 0; i < number; i++) {
        let selectElement = $(dropdown_field_id+'_'+i);
        configureDropdown(selectElement, number, updateFunc, dropdown_field_id);

        $('#id_row_field_'+i).on('change', updateFunc);
        $('#id_column_field_'+i).on('change', updateFunc);
        $('#id_size_field_'+i).on('change', updateFunc);
    }
}

/**
 *
 * @param visible_buttons
 */
function initializeAddAndRemoveButtons(row_id, dropdown_id, visible_buttons=1) {
    let addButton = $('#button-id-add_row');
    let removeButton = $('#button-id-remove_row');

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
            $('#id_row_field_'+visible_buttons).val("");
            $('#id_column_field_'+visible_buttons).val("");
            $('#id_size_field_'+visible_buttons).val("");
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