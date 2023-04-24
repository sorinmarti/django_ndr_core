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
function getMaskedUrl(baseUrl) {
    let data_array = [];
    for (let i = 0; i < 20; i++) {
        let row_field =  $('#id_row_field_'+i);
        let column_field =  $('#id_column_field_'+i);
        let size_field = $('#id_size_field_'+i);
        let search_field = $('#id_search_field_'+i);
        data_array[i]=row_field.val()+"~"+column_field.val()+"~"+size_field.val()+"~"+search_field.val();
    }
    return baseUrl.replace("image_string", data_array);
}

/**
 * This function is used to configure the rows for the form. It loops through the number of rows and configures the
 * dropdowns for each row. It also adds the change event to the row, column and size fields.
 * @param number - The number of rows to configure
 * @param imageBaseUrl - The base url for the preview image. It must contain the string "image_string"
 */
function configureRows(number, imageBaseUrl) {
    /**
     * This function is used to update the preview image. It gets the masked url and updates the src attribute of the
     * preview image.
     */
    let updateFunc = function updateImage() {
        let previewImage = $('#preview_image');
        let maskedUrl = getMaskedUrl(imageBaseUrl);
        previewImage.attr('src', maskedUrl);
    }

    for (let i = 0; i < number; i++) {
        let selectElement = $('#id_search_field_'+i);
        configureDropdown(selectElement, number, updateFunc);

        $('#id_row_field_'+i).on('change', updateFunc);
        $('#id_column_field_'+i).on('change', updateFunc);
        $('#id_size_field_'+i).on('change', updateFunc);
    }
}

function configureDropdown(selectElement, totalElements, updateFunc) {

    selectElement.change(function(e) {
        let before_change = $(this).data('pre');//get the pre data
        $(this).data('pre', $(this).val());//update the pre data
        let after_change = $(this).data('pre');//get the pre data
        let this_index = this.id.split('_').slice(-1);
        if(before_change !== '') {
            for (let x = 0; x < totalElements; x++) {
                if(x !== parseInt(this_index)) {
                    $('#id_search_field_'+x+' option[value="'+before_change+'"]').removeAttr("disabled");
                }
            }
        }
        if(after_change !== '') {
            for (let x = 0; x < totalElements; x++) {
                if(x !== parseInt(this_index)) {
                    $('#id_search_field_'+x+' option[value="'+after_change+'"]').attr("disabled", "disabled");
                }
            }
        }

        // Update the image
        updateFunc();
    });
}

function initializeAddAndRemoveButtons() {
    let addButton = $('#button-id-add_row');
    let removeButton = $('#button-id-remove_row');

    // Set visible buttons to 1
    let visible_buttons = 0;

    addButton.on('click', function () {
        removeButton.show();
        if (visible_buttons < 19) {
            visible_buttons += 1;
            $('#search_field_config_row_' + visible_buttons).show();
        }
        if (visible_buttons === 19) {
            addButton.hide();
        }

        //console.log(visible_buttons);
    });

    removeButton.on('click', function () {
        if(visible_buttons > 0) {
            let sField = $('#id_search_field_'+visible_buttons);
            sField.val(null);
            sField.change();
            $('#id_row_field_'+visible_buttons).val("");
            $('#id_column_field_'+visible_buttons).val("");
            $('#id_size_field_'+visible_buttons).val("");
            $('#search_field_config_row_'+visible_buttons).hide();

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