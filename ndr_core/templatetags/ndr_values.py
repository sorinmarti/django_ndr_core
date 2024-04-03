"""Template tags for NDR Core."""
from django import template
from django.utils.translation import get_language

from ndr_core.models import NdrCoreValue, NdrCoreImage, get_available_languages
from ndr_core.ndr_settings import NdrSettings

register = template.Library()


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
    """Returns the path to the logo image."""
    try:
        logo_image = NdrCoreImage.objects.get(
            image_group=NdrCoreImage.ImageGroup.PAGE_LOGOS, language=get_language()
        ).image.url
    except NdrCoreImage.DoesNotExist:
        try:
            logo_image = NdrCoreImage.objects.filter(
                image_group=NdrCoreImage.ImageGroup.PAGE_LOGOS
            )
            if logo_image:
                logo_image = logo_image.first().image.url
            else:
                logo_image = "static/ndr_core/images/logo.png"
        except NdrCoreImage.DoesNotExist:
            logo_image = "static/ndr_core/images/logo.png"
    return logo_image
