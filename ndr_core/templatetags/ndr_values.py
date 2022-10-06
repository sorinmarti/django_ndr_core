from django import template

from ndr_core.models import NdrCoreValue

register = template.Library()


@register.simple_tag(name='config_value')
def get_config_value(name):
    try:
        value = NdrCoreValue.objects.get(value_name=name)
        return value.value_value
    except NdrCoreValue.DoesNotExist:
        return None