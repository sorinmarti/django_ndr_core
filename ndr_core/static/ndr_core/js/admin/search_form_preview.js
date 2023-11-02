function init_preview(imageBaseUrl) {
    configureRows(20, imageBaseUrl, '#id_search_field', '#preview_search_form_image');

    let visible_buttons = 1;
    for(let i = 1; i < 20; i++){
        if($('#id_search_field_' + i).val() === '') {
            $('#search_field_config_row_' + i).hide();
        }
        else {
            visible_buttons++;
        }
    }

    initializeAddAndRemoveButtons('#search_field_config_row', '#id_search_field', visible_buttons);

    let maskedUrl = getMaskedUrl(imageBaseUrl, '#id_search_field');
    let previewImage = $('#preview_search_form_image');
    previewImage.attr('src', maskedUrl);
}