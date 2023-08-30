from django import template
from django.utils.translation import get_language

from ndr_core.models import NdrCoreValue, NdrCoreImage
from ndr_core.ndr_settings import NdrSettings

register = template.Library()


@register.simple_tag(name='config_value')
def get_config_value(name):
    try:
        value = NdrCoreValue.objects.get(value_name=name)
        return value.get_value()
    except NdrCoreValue.DoesNotExist:
        return ''


@register.simple_tag(name='translated_config_value')
def get_translated_value(name):
    try:
        value = NdrCoreValue.objects.get(value_name=name)
        return value.translated_value()
    except NdrCoreValue.DoesNotExist:
        return ''


@register.simple_tag(name='settings_value')
def get_version(name):
    if name.lower() == "version":
        return NdrSettings.get_version()
    return ''


@register.simple_tag(name='ndr_available_languages')
def get_available_languages():
    try:
        base_language = NdrCoreValue.objects.get(value_name='ndr_language')
        additional_languages = NdrCoreValue.objects.get(value_name='available_languages')
        langs = [base_language.get_value()]
        for lang in additional_languages.get_value():
            langs.append(lang)

        return langs
    except NdrCoreValue.DoesNotExist:
        return ''


@register.simple_tag(name='logo_image_path')
def get_logo_image_path():
    try:
        logo_image = NdrCoreImage.objects.get(image_group=NdrCoreImage.ImageGroup.PAGE_LOGOS,
                                              language=get_language()).image.url
    except NdrCoreImage.DoesNotExist:
        print("No logo image found for language " + get_language())
        logo_image = NdrSettings.get_static_path() + 'images/logo.png'
    return logo_image
