
function setComponents(select_value) {
    let search_configs = $('#div_id_search_configs');
    let list_configs = $('#div_id_list_configs');
    let template_text = $('#div_id_template_text');
    let simple_api = $('#div_id_simple_api');

    switch (select_value) {
            case '1':   // Template Page
                search_configs.hide();
                list_configs.hide();
                template_text.show();
                simple_api.hide();
                break;
            case '2':   // Simple Search
                search_configs.hide();
                list_configs.hide();
                template_text.hide();
                simple_api.show();
                break;
            case '5':   // Contact Page
                search_configs.hide();
                list_configs.hide();
                template_text.hide();
                simple_api.hide();
                break;
            case '3':   // Custom Search
                search_configs.show();
                list_configs.hide();
                template_text.hide();
                simple_api.hide();
                break;
            case '4':   // Combined Search
                search_configs.show();
                list_configs.hide();
                template_text.hide();
                simple_api.show();
                break;
            case '6':   // Filterable List
                search_configs.hide();
                list_configs.show();
                template_text.hide();
                simple_api.hide();
                break;
        }
}
$(document).ready(function() {
    setComponents($('#id_page_type').val())
    $('#id_page_type').change(function() {
        setComponents(this.value)
    });
});
