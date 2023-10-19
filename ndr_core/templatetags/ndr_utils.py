import re
import urllib

from django import template
from django.utils.translation import get_language

from ndr_core.models import NdrCoreSearchField, NdrCoreValue

register = template.Library()


@register.inclusion_tag('ndr_core/dummy.html')
def render_result(result_object, api_config):
    """Renders a result object using the appropriate template."""
    render_template = 'ndr_core/result_renderers/default_template.html'
    return {'template': render_template,
            'result': result_object}


@register.filter
def key_value(data_dict, key):
    """Provides key-value lookup functionality in templates."""
    if data_dict is None:
        return ''
    try:
        return data_dict[key]
    except KeyError:
        return ''


@register.filter
def is_list(value):
    """Provides key-value lookup functionality in templates."""
    return type(value) is list


@register.filter
def modulo(num, val):
    """Provides modulo functionality in templates."""
    return num % val


@register.filter
def url_parse(value):
    """Provides modulo functionality in templates."""
    if value is None:
        return ''

    return value.replace('/', '_sl_')


@register.filter
def url_deparse(value):
    """Provides modulo functionality in templates."""
    if value is None:
        return ''

    # return urllib.parse.unquote(value)
    return value.replace('_sl_', '/')


@register.filter
def reduce_iiif_size(image_url, target_percent_of_size):
    """Reduces the size of an IIIF image URL."""
    if image_url is None:
        return ''
    if type(image_url) is not str:
        return ''
    if target_percent_of_size is None:
        return image_url

    if '/full/full/' in image_url:
        return image_url.replace('/full/full/', f'/full/pct:{target_percent_of_size}/')
    match = re.match(r'^.*\/(\d*,\d*,\d*,\d*)\/(full)/.*$', image_url)
    if match:
        return image_url.replace(match.group(2), f'pct:{target_percent_of_size}')


@register.filter
def translate_dict_value(key_to_translate, dict_name):
    return translate_dict_foo(key_to_translate, dict_name, 'value')


@register.filter
def translate_dict_info(key_to_translate, dict_name):
    return translate_dict_foo(key_to_translate, dict_name, 'info')


def translate_dict_foo(key_to_translate, dict_name, target_key):
    """Translates a value in a dictionary."""
    if key_to_translate is None:
        return ''

    try:
        field = NdrCoreSearchField.objects.get(field_name=dict_name)

        choices = field.get_list_choices_as_dict()

        default_language = NdrCoreValue.objects.get(value_name='ndr_language').get_value()
        additional_languages = NdrCoreValue.objects.get(value_name="available_languages").get_value()
        selected_language = get_language()

        if key_to_translate in choices:
            value_object = choices[key_to_translate]

            if selected_language == default_language:
                return value_object[target_key]
            elif selected_language in additional_languages:
                key = f'{target_key}_{selected_language}'
                if key in value_object:
                    return value_object[key]

            return f'{key_to_translate} (TNF)'

        return f'{key_to_translate} (KNF)'
    except NdrCoreSearchField.DoesNotExist:
        return f'{key_to_translate} (VNF)'


@register.filter
def translate_to_color(value, lightness=50):
    """Translates a value to a color."""
    if value is None:
        return ''

    hash_value = 0
    for char in value:
        hash_value = ord(char) + ((hash_value << 5) - hash_value)
        hash_value = hash_value & hash_value

    return f'hsl({hash_value%360}, {100}%, {lightness}%)'


@register.filter
def format_date(date_string):
    """Formats a date string."""
    if date_string is None:
        return ''

    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_string):
        split_date = date_string.split('-')
        return f'{split_date[2]}.{split_date[1]}.{split_date[0]}'
    return date_string


@register.filter
def clean_list(list_object):
    """Formats a list object."""
    if list_object is None:
        return []

    type_of_list = type(list_object)
    if type_of_list is list:
        return list_object
    if type_of_list is str:
        return [list_object]
