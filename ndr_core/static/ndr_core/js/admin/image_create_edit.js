
function setComponents(select_value) {
    let select_help_text = $('#hint_id_image_group');
    let info = $('#id_info_box');
    let language = $('#div_id_language');
    let citation = $('#div_id_citation');
    let url = $('#div_id_url');
    let url_help = $('#hint_id_url');
    let title = $('#div_id_title');
    let title_help = $('#hint_id_title');
    let caption = $('#div_id_caption');
    let caption_help = $('#hint_id_caption');
    let image = $('#div_id_image');

    let page_title = $('#id_page_title');

    switch (select_value) {
        case 'page_logos':
            language.show();
            citation.hide();
            url.hide();
            title.hide();
            caption.hide();
            image.show();
            page_title.text('Page Logo');
            select_help_text.text('Page logos for your site');
            info.text('Your Page has one logo which is displayed in the header and footer of the page.' +
                'You can upload a logo for each language you have enabled. ' +
                'If you do not upload a logo for a language, the logo of the default language will be used.' +
                'If you do not upload a logo at all, the NDR-Core logo will be used.');
            break;
        case 'backgrounds':   // backgrounds
            language.hide();
            citation.hide();
            url.hide();
            title.hide();
            caption.hide();
            image.show();
            page_title.text('Background Image');
            select_help_text.text('Background images for your site');
            info.text('You can upload multiple background images and use them in different pages. ' +
                'You don\'t need background images for a page, but if you want to use them, ' +
                'you can select them in the page settings.');
            break;
        case 'elements':   // elements
            language.hide();
            citation.hide();
            url.hide();
            title.hide();
            caption.hide();
            image.show();
            page_title.text('Slideshow Image');
            select_help_text.text('Images to use in slideshows.');
            info.text('You can upload images and use them in UI Elements such as ' +
                'slideshows, banners, etc. ');
            break;
        case 'figures':   // figures
            language.hide();
            citation.show();
            url_help.text('The URL, the figure should link to');
            url.show();
            title.children('label').text('Title');
            title_help.text('The title of the figure');
            title.show();
            caption.children('label').text('Caption');
            caption_help.text('The caption of the figure');
            caption.show();
            image.show();
            page_title.text('Figure');
            select_help_text.text('Figures with captions');
            info.text('You can upload images and use them in your pages. ' +
                'You can add a title, a caption and a citation to each image.');
            break;
        case 'logos':   // logos
            language.hide();
            citation.hide();
            url_help.text('The URL, the logo should link to');
            url.show();
            title.hide();
            caption.hide();
            image.show();
            page_title.text('Logo');
            select_help_text.text('Logos of project partners');
            info.text('You can upload logos of project partners and link to their websites. ' +
                'The footer of the page will automatically generate a list of project partners');
            break;
        case 'people':   // people
            language.hide();
            citation.hide();
            url_help.text('The URL, the project member should link to.');
            url.show();
            title.children('label').text('Name');
            title_help.text('The name of the project member');
            title.show();
            caption.children('label').text('Role/Description');
            caption_help.text('The role or description of the project member');
            caption.show();
            image.show();
            page_title.text('Project Member');
            select_help_text.text('Images of project members');
            info.text('You can upload images of project members and use them in the people section. ' +
                'You can automatically generate a list of project members by selecting the ' +
                '"About us" page type in the page settings.');
            break;
        default:
            language.hide();
            citation.hide();
            url.hide();
            title.hide();
            caption.hide();
            image.hide();
            page_title.text('Image');
            select_help_text.text('Select the image group you want to add images to');
            info.text('Select the image group you want to add images to');
            break;
    }
}
$(document).ready(function() {
    setComponents($('#id_image_group').val())
    $('#id_image_group').change(function() {
        setComponents(this.value)
    });
});
