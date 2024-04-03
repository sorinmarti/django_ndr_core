
function setTabs(select_value) {
    // Get the first tab and all other tabs
    let first_tab = $("#my-tab-holder li:first");  //get the first tab
    let other_tabs = $("#my-tab-holder li:not(:first)");  //get all tabs except first tab

    // If no UI-Element is selected, disable all tabs
    if (select_value === '') {
        first_tab.children('a').text('Select a UI-Element');
        $(other_tabs).each(function(k,v){
            $(this).children('a').attr('class', 'nav-link disabled');
            $(this).children('a').text('');
        });
        $( ".tab-pane" ).attr( "style", "display: none;" );
        return;
    }

    // Otherwise, enable all tabs
    $( ".tab-pane" ).removeAttr( "style" );
    first_tab.children('a').tab('show');

    // These UI-Elements feature 1 tab
    if(['card', 'jumbotron', 'iframe', 'banner', 'manifest_viewer'].includes(select_value)) {
        first_tab.children('a').text('Configure your ' + select_value);
        $(other_tabs).each(function(k,v){
            $(this).children('a').attr('class', 'nav-link disabled');
            $(this).children('a').text('');
        });

        let first_ndr_banner_image = $('#div_id_item_0_ndr_banner_image');
        let first_ndr_slide_image = $('#div_id_item_0_ndr_slide_image');
        let first_ndr_card_image = $('#div_id_item_0_ndr_card_image');
        let first_title = $('#div_id_item_0_title');
        let first_text = $('#div_id_item_0_text');
        let first_url = $('#div_id_item_0_url');
        let first_manifest_group = $('#div_id_item_0_manifest_group');

        switch (select_value) {
            case 'card':
                first_ndr_banner_image.hide();
                first_ndr_slide_image.hide();
                first_ndr_card_image.show();
                first_title.show();
                first_text.show();
                first_url.show();
                first_manifest_group.hide();
                break;
            case 'jumbotron':
                first_ndr_banner_image.show();
                first_ndr_slide_image.hide();
                first_ndr_card_image.hide();
                first_title.show();
                first_text.show();
                first_url.hide();
                first_manifest_group.hide();
                break;
            case 'iframe':
                first_ndr_banner_image.hide();
                first_ndr_slide_image.hide();
                first_ndr_card_image.hide();
                first_title.hide();
                first_text.show();
                first_url.hide();
                first_manifest_group.hide();
                break;
            case 'banner':
                first_ndr_banner_image.show();
                first_ndr_slide_image.hide();
                first_ndr_card_image.hide();
                first_title.hide();
                first_text.hide();
                first_url.hide();
                first_manifest_group.hide();
                break;
            case 'manifest_viewer':
                first_ndr_banner_image.hide();
                first_ndr_slide_image.hide();
                first_ndr_card_image.hide();
                first_title.hide();
                first_text.hide();
                first_url.hide();
                first_manifest_group.show();
                break;
        }
    }
    // The other UI-Elements feature 10 tabs
    else {
        first_tab.children('a').text('Slide 1');
        $(other_tabs).each(function(k,v){
            $(this).children('a').attr('class', 'nav-link');
            $(this).children('a').text('Slide ' + (k+2));
        });

        for (let i = 0; i < 10; i++) {
            let ndr_banner_image = $('#div_id_item_' + i + '_ndr_banner_image');
            let ndr_slide_image = $('#div_id_item_' + i + '_ndr_slide_image');
            let ndr_card_image = $('#div_id_item_' + i + '_ndr_card_image');
            let title = $('#div_id_item_' + i + '_title');
            let text = $('#div_id_item_' + i + '_text');
            let url = $('#div_id_item_' + i + '_url');
            let manifest_group = $('#div_id_item_' + i + '_manifest_group');

            switch (select_value) {
            case 'slides':
                ndr_banner_image.hide();
                ndr_slide_image.show();
                ndr_card_image.hide();
                title.hide();
                text.hide();
                url.hide();
                manifest_group.hide();
                break;
            case 'carousel':
                ndr_banner_image.hide();
                ndr_slide_image.show();
                ndr_card_image.hide();
                title.show();
                text.show();
                url.hide();
                manifest_group.hide();
                break;
            }
        }

    }
}

function setComponents(select_value) {
    let select_help_text = $('#hint_id_type');

    let ui_element_preview = $('#id_ui_element_preview');
    let show_indicators = $('#id_show_indicators');
    let link_element = $('#id_link_element');
    let autoplay = $('#id_autoplay');

    let new_preview_image_url = '';
    ui_element_preview.attr('src', new_preview_image_url);
    let preview_image_url = "/static/ndr_core/images/admin/ui_elements/_ITEM_.png";

    setTabs(select_value);

    switch (select_value) {
        case 'card':    // card
            select_help_text.text('A Card can feature an image, a title, some text and a link');
            new_preview_image_url = preview_image_url.replace('_ITEM_', 'card');
            ui_element_preview.attr('src', new_preview_image_url);

            show_indicators.prop( "disabled", true );
            link_element.prop( "disabled", false );
            autoplay.prop( "disabled", true );
            break;
        case 'slides':   // slides
            select_help_text.text('A Slideshow features images');
            new_preview_image_url = preview_image_url.replace('_ITEM_', 'slides');
            ui_element_preview.attr('src', new_preview_image_url);

            show_indicators.prop( "disabled", false );
            link_element.prop( "disabled", true );
            autoplay.prop( "disabled", false );
            break;
        case 'carousel':   // carousel
            select_help_text.text('A carousel is a slideshow with text');
            new_preview_image_url = preview_image_url.replace('_ITEM_', 'carousel');
            ui_element_preview.attr('src', new_preview_image_url);

            show_indicators.prop( "disabled", false );
            link_element.prop( "disabled", true );
            autoplay.prop( "disabled", false );
            break;
        case 'jumbotron':   // jumbotron
            select_help_text.text('A jumbotron is a large callout which can feature a background image and text');
            new_preview_image_url = preview_image_url.replace('_ITEM_', 'jumbotron');
            ui_element_preview.attr('src', new_preview_image_url);

            show_indicators.prop( "disabled", true );
            link_element.prop( "disabled", true );
            autoplay.prop( "disabled", true );
            break;
        case 'iframe':   // iframe
            select_help_text.text('An iframe is a container for a web page');
            new_preview_image_url = preview_image_url.replace('_ITEM_', 'iframe');
            ui_element_preview.attr('src', new_preview_image_url);

            show_indicators.prop( "disabled", true );
            link_element.prop( "disabled", true );
            autoplay.prop( "disabled", true );
            break;
        case 'banner':   // banner
            select_help_text.text('A banner is a large callout which can feature an image');
            new_preview_image_url = preview_image_url.replace('_ITEM_', 'banner');
            ui_element_preview.attr('src', new_preview_image_url);

            show_indicators.prop( "disabled", true );
            link_element.prop( "disabled", true );
            autoplay.prop( "disabled", true );
            break;
        case 'manifest_viewer':   // manifest_viewer
            select_help_text.text('A manifest viewer is a viewer for a IIIF manifest');
            new_preview_image_url = preview_image_url.replace('_ITEM_', 'manifest_viewer');
            ui_element_preview.attr('src', new_preview_image_url);

            show_indicators.prop( "disabled", true );
            link_element.prop( "disabled", true );
            autoplay.prop( "disabled", true );
            break;
        default:
            select_help_text.text('Select the image group you want to add images to');
            new_preview_image_url = preview_image_url.replace('_ITEM_', 'none');
            ui_element_preview.attr('src', new_preview_image_url);
            break;
    }
}

function show_item_preview(item_id, number) {
    let selected_value = $(item_id).val();

    if(selected_value === '') {
        return;
    }

    $.ajax({
        url: '/ndr_core/preview/image/' + selected_value + '/',
        success: function(data) {
            let preview_id = '#id_ui_element_' + number + '_preview';
            $(preview_id).attr('src', data);
        }
    });
}

$(document).ready(function() {

    setComponents($('#id_type').val())
    $('#id_type').change(function() {
        setComponents(this.value)
    });

    for(let i = 0; i < 10; i++) {
        let item_banner_name = '#id_item_' + i + '_ndr_banner_image';
        let item_slide_name = '#id_item_' + i + '_ndr_slide_image';
        let item_card_name = '#id_item_' + i + '_ndr_card_image';

        show_item_preview(item_banner_name, i);
        show_item_preview(item_slide_name, i);
        show_item_preview(item_card_name, i);

        $(item_banner_name).change(function() {
            show_item_preview(item_banner_name, i);
        });
        $(item_slide_name).change(function() {
            show_item_preview(item_slide_name, i);
        });
        $(item_card_name).change(function() {
            show_item_preview(item_card_name, i);
        });
    }
});
