
function setComponents(select_value) {
    switch (select_value) {
            case '1':   // Template Page
            case '2':   // Simple Search
            case '5':   // Contact Page
                $('#div_id_search_configs').hide();
                $('#div_id_list_configs').hide();
                break;
            case '3':   // Custom Search
            case '4':   // Combined Search
                $('#div_id_search_configs').show();
                $('#div_id_list_configs').hide();
                break;
            case '6':   // Filterable List
                $('#div_id_search_configs').hide();
                $('#div_id_list_configs').show();
                break;
        }
}
$(document).ready(function() {
    setComponents($('#id_page_type').val())
    $('#id_page_type').change(function() {
        setComponents(this.value)
    });
});
