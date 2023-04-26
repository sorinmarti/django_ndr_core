from django import template

from ndr_core.models import NdrCoreValue
from ndr_core.ndr_settings import NdrSettings

register = template.Library()


@register.simple_tag(name='config_value')
def get_config_value(name):
    try:
        value = NdrCoreValue.objects.get(value_name=name)
        return value.get_value()
    except NdrCoreValue.DoesNotExist:
        return ''


@register.simple_tag(name='settings_value')
def get_version(name):
    if name.lower() == "version":
        return NdrSettings.get_version()
    return ''
