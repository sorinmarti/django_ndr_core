function init_search_form_preview(imageBaseUrl) {
    let dropdown_field_id = '#id_search_field';
    let image_field_id = '#preview_search_form_image';
    let result_field_config_row_stub = '#search_field_config_row';
    let row_field_id = '#id_row_field';
    let column_field_id = '#id_column_field';
    let size_field_id = '#id_size_field';
    let add_button_id = '#button-id-add_row';
    let remove_button_id = '#button-id-remove_row';

   init_preview(
       imageBaseUrl,
       dropdown_field_id,
       image_field_id,
       result_field_config_row_stub,
       row_field_id,
       column_field_id,
       size_field_id,
       add_button_id,
       remove_button_id);
}