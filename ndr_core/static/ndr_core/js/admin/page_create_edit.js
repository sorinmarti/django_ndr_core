
function setComponents(select_value) {
    let search_configs = $('#div_id_search_configs');
    let list_configs = $('#div_id_list_configs');
    let template_text = $('#div_id_template_text');
    let simple_api = $('#div_id_simple_api');
    let info_text = $('#page_type_info')

    switch (select_value) {
            case '1':   // Template Page
                search_configs.hide();
                list_configs.hide();
                template_text.show();
                simple_api.hide();
                info_text.text('Creates a page with static content. You can add your content and UI elements in the ' +
                               'editor below. Refer to the help pages on how to use UI elements.')
                break;
            case '2':   // Simple Search
                search_configs.hide();
                list_configs.hide();
                template_text.hide();
                simple_api.show();
                info_text.text('Creates a page with a simple catch-all search field form. Choose an API configuration ' +
                               'and display a simple search form.')
                break;
            case '5':   // Contact Page
                search_configs.hide();
                list_configs.hide();
                template_text.show();
                simple_api.hide();
                info_text.text('Creates a page with a contact form. Users can send you messages which you can read in ' +
                               'the administration interface or forward to an email-address..')
                break;
            case '3':   // Custom Search
                search_configs.show();
                list_configs.hide();
                template_text.hide();
                simple_api.hide();
                info_text.text('Creates a page with one or multiple custom search forms. You need to create these forms ' +
                               'before you can use this page type. Multiple forms are displayed in tabs.')
                break;
            case '4':   // Combined Search
                search_configs.show();
                list_configs.hide();
                template_text.hide();
                simple_api.show();
                info_text.text('Creates a page with tabs with a simple and a custom search form. Refer to the help pages ' +
                               'on how to create search forms.')
                break;
            case '6':   // Filterable List
                search_configs.hide();
                list_configs.show();
                template_text.hide();
                simple_api.hide();
                info_text.text('Not implemented yet')
                break;
            case '7':   // Flip Book
                search_configs.hide();
                list_configs.hide();
                template_text.hide();
                simple_api.hide();
                info_text.text('Creates an "empty" page with with "next" and "previous" buttons. You can add pages with ' +
                               'this page as parent and they will be in the list to be flipped through.')
                break;
            case '8':   // About Us
                search_configs.hide();
                list_configs.hide();
                template_text.show();
                simple_api.hide();
                info_text.text('Create an about us page with images from your "people images group" and template text ' +
                               'you can add in the editor below.')
                break;
        }
}
$(document).ready(function() {
    setComponents($('#id_page_type').val())
    $('#id_page_type').change(function() {
        setComponents(this.value)
    });
});
