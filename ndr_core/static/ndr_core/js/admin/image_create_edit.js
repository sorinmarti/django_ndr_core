
function setComponents(select_value) {
    let select_help_text = $('#hint_id_image_group');
    let language = $('#div_id_language');
    let citation = $('#div_id_citation');
    let url = $('#div_id_url');
    let title = $('#div_id_title');
    let caption = $('#div_id_caption');
    let image = $('#div_id_image');

    switch (select_value) {
        case 'page_logos':
            language.show();
            citation.hide();
            url.hide();
            title.hide();
            caption.hide();
            image.show();

            select_help_text.text('Header images for your site');
            break;
        case 'backgrounds':   // backgrounds
            language.hide();
            citation.hide();
            url.hide();
            title.hide();
            caption.hide();
            image.show();

            select_help_text.text('Background images for your site');
            break;
        case 'elements':   // elements
            language.hide();
            citation.hide();
            url.hide();
            title.hide();
            caption.hide();
            image.show();

            select_help_text.text('UI Elements such as carousels, etc.');
            break;
        case 'figures':   // figures
            language.hide();
            citation.show();
            url.show();
            title.show();
            caption.show();
            image.show();

            select_help_text.text('Figures with captions');
            break;
        case 'logos':   // logos
            language.hide();
            citation.hide();
            url.show();
            title.show();
            caption.show();
            image.show();

            select_help_text.text('Logos of project partners');
            break;
        case 'people':   // people
            language.hide();
            citation.hide();
            url.show();
            title.show();
            caption.show();
            image.show();

            select_help_text.text('Images of project members');
            break;
        default:
            language.hide();
            citation.hide();
            url.hide();
            title.hide();
            caption.hide();
            image.hide();

            select_help_text.text('Select the image group you want to add images to');
            break;
    }
}
$(document).ready(function() {
    setComponents($('#id_image_group').val())
    $('#id_image_group').change(function() {
        setComponents(this.value)
    });
});
