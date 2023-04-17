function getMaskedUrl(baseUrl) {
    let data_array = [];
    for (let i = 0; i < 20; i++) {
        let row_field =  $('#id_row_field_'+i)
        let column_field =  $('#id_column_field_'+i)
        let size_field = $('#id_size_field_'+i);
        let search_field = $('#id_search_field_'+i);
        data_array[i]=row_field.val()+"~"+column_field.val()+"~"+size_field.val()+"~"+search_field.val();
    }
    let url_mask = baseUrl.replace("image_string", data_array);
    return url_mask;
}