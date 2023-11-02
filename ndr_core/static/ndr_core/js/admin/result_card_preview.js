function init_preview(imageBaseUrl) {
    configureRows(20, imageBaseUrl, '#id_result_field', '#preview_result_card_image' );

    let visible_buttons = 1;
    for(let i = 1; i < 20; i++){
        if($('#id_result_field_' + i).val() === '') {
            $('#result_field_config_row_' + i).hide();
        }
        else {
            visible_buttons++;
        }
    }

    initializeAddAndRemoveButtons('#result_field_config_row', '#id_result_field', visible_buttons);

    let maskedUrl = getMaskedUrl(imageBaseUrl, '#id_result_field');
    let previewImage = $('#preview_result_card_image');
    previewImage.attr('src', maskedUrl);
}