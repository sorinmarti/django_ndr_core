
function setComponents(select_value) {
    let select_help_text = $('#hint_id_type');
    let type = $('#div_id_type');
    let title = $('#div_id_title');
    let use_image_conf = $('#div_id_use_image_conf');
    let show_indicators = $('#div_id_show_indicators');
    let show_title = $('#div_id_show_title');
    let show_text = $('#div_id_show_text');
    let show_image = $('#div_id_show_image');
    let link_element = $('#div_id_link_element');
    let autoplay = $('#div_id_autoplay');

    switch (select_value) {
        case 'card':    // card
            select_help_text.text('Header images for your site');
            break;
        case 'slides':   // slides
            select_help_text.text('Background images for your site');
            break;
        case 'carousel':   // carousel
            select_help_text.text('UI Elements such as carousels, etc.');
            break;
        case 'jumbotron':   // jumbotron
            select_help_text.text('Figures with captions');
            break;
        case 'iframe':   // iframe
            select_help_text.text('An iframe');
            break;
        case 'banner':   // banner
            select_help_text.text('A banner with an image');
            break;
        default:
            select_help_text.text('Select the image group you want to add images to');
            break;
    }
}
$(document).ready(function() {
    setComponents($('#id_type').val())
    $('#id_type').change(function() {
        setComponents(this.value)
    });
});
