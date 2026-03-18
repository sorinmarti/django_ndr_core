"""Template tags for NDR Core."""
from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

from ndr_core.models import NdrCoreValue, NdrCoreImage, get_available_languages
from ndr_core.ndr_settings import NdrSettings

register = template.Library()


@register.filter(name='render_settings', is_safe=True)
def render_settings(text):
    """Replaces [[setting|name]] tags in a string with their stored values."""
    from ndr_core.ndr_template_tags import TextPreRenderer
    if not text:
        return text
    return mark_safe(TextPreRenderer(str(text), None).create_settings())


@register.simple_tag(name="config_value")
def get_config_value(name):
    """Returns the value of a configuration value."""
    try:
        value = NdrCoreValue.objects.get(value_name=name)
        return value.get_value()
    except NdrCoreValue.DoesNotExist:
        return ""


@register.simple_tag(name="translated_config_value")
def get_translated_value(name):
    """Returns the translated value of a config value."""
    try:
        value = NdrCoreValue.objects.get(value_name=name)
        return value.translated_value()
    except NdrCoreValue.DoesNotExist:
        return ""


@register.simple_tag(name="settings_value")
def get_version(name):
    """Returns the version of the NDR Core."""
    if name.lower() == "version":
        return NdrSettings.get_version()
    return ""


@register.simple_tag(name="ndr_available_languages")
def tag_get_available_languages():
    """Returns a list of available languages."""
    return [('en', 'English')] + get_available_languages()


@register.simple_tag(name="logo_image_path")
def get_logo_image_path():
    """Returns the path to the logo image based on current language settings."""
    import json
    from ndr_core.models import NdrCoreValue

    # Get page logos from settings
    page_logos_setting = NdrCoreValue.get_or_initialize('page_logo_images')
    try:
        page_logos_data = json.loads(page_logos_setting.value_value) if page_logos_setting.value_value else {}
    except (json.JSONDecodeError, ValueError):
        page_logos_data = {}

    # Try to get logo for current language
    current_lang = get_language()
    logo_id = page_logos_data.get(current_lang)

    # If no logo for current language, try base language
    if not logo_id:
        base_lang_setting = NdrCoreValue.get_or_initialize('ndr_language')
        base_lang = base_lang_setting.get_value()
        logo_id = page_logos_data.get(base_lang)

    # Get the image object
    if logo_id:
        try:
            logo_image = NdrCoreImage.objects.get(pk=logo_id, image_active=True)
            return logo_image.image.url
        except NdrCoreImage.DoesNotExist:
            pass

    # Default logo if none configured
    return "static/ndr_core/images/logo.png"
