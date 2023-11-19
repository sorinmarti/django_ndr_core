"""Template tags for the ndr_core app."""
import json
import re

from django import template
from django.db.models import Max
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

from ndr_core.models import NdrCoreSearchField, NdrCoreValue, NdrCoreResultField

register = template.Library()


@register.tag(name='render_result')
def render_result_tag(parser, token):
    """Renders a result object."""
    token_list = token.split_contents()
    return RenderResultNode(token_list[1], token_list[2], token_list[3])


class RenderResultNode(template.Node):
    """Renders a result object."""

    def __init__(self, result, search_config, result_card_group='normal'):
        self.result = template.Variable(result)
        self.search_config = template.Variable(search_config)
        self.result_card_group = template.Variable(result_card_group)

    def create_card(self, context, result):
        """Creates a result card."""
        card_context = {"result": result,
                        "card_content": self.create_grid(context, result['data'])}
        card_template = 'ndr_core/result_renderers/configured_fields_template.html'

        card_template_str = get_template(card_template).render(card_context)
        return mark_safe(card_template_str)

    def create_grid(self, context, data):
        """Creates a grid of result fields."""
        row_template = 'ndr_core/result_renderers/elements/result_row.html'
        result_card_fields = self.search_config.resolve(context).result_card_fields.filter(result_card_group=self.result_card_group.resolve(context))
        max_row = result_card_fields.aggregate(Max('field_row'))

        card_grid_str = ''
        for row in range(max_row['field_row__max']):
            row += 1
            fields = []
            for column in result_card_fields.filter(field_row=row).order_by('field_column'):
                field_html = self.create_field(column, data)
                fields.append(field_html)
            row_context = {"fields": fields}
            row_template_str = get_template(row_template).render(row_context)
            card_grid_str += row_template_str

        return mark_safe(card_grid_str)

    @staticmethod
    def safe_format_string(string, data):
        """Formats a string and returns it as safe."""
        try:
            return mark_safe(string.format(**data))
        except KeyError:
            return 'KeyError: The key does not exist in the data.'
        except AttributeError:
            return 'AttributeError: The key is malformed'
        except TypeError:
            return 'TypeError'
        except ValueError:
            return 'ValueError'
        except IndexError:
            return 'IndexError'

    def create_image_field(self, string, data):
        """Creates an image field."""
        src = self.safe_format_string(string, data)
        return mark_safe(f'<img src="{src}" class="img-fluid" alt="Image">')

    def create_field(self, field, data):
        """Creates a result field."""
        field_template = 'ndr_core/result_renderers/elements/result_field.html'
        r_field = field.result_field

        field_content = ''
        if r_field.field_type == NdrCoreResultField.FieldType.STRING:
            field_content = self.safe_format_string(r_field.expression, data)
        elif r_field.field_type == NdrCoreResultField.FieldType.RICH_STRING:
            field_content = self.safe_format_string(r_field.rich_expression, data)
        elif r_field.field_type == NdrCoreResultField.FieldType.IMAGE:
            field_content = self.create_image_field(r_field.expression, data)
        elif r_field.field_type == NdrCoreResultField.FieldType.IIIF_IMAGE:
            field_content = self.create_image_field(r_field.expression, data)
        elif r_field.field_type == NdrCoreResultField.FieldType.TABLE:
            field_content = "Not implemented yet."
        elif r_field.field_type == NdrCoreResultField.FieldType.MAP:
            field_content = "Not implemented yet."

        field_context = {"size": field.field_size,
                         "border": "border" if r_field.display_border else "",
                         "field_content": field_content}
        field_template_str = get_template(field_template).render(field_context)
        return mark_safe(field_template_str)

    def render(self, context):
        """Renders a result object."""
        result_object = self.result.resolve(context)
        num_result_fields = self.search_config.resolve(context).result_card_fields.all().count()

        html_string = ''
        for result in result_object.results:
            if num_result_fields > 0:
                html_string += self.create_card(context, result)
            else:
                # No result card fields configured, so we render the result as pretty json
                print("INFO: No result card fields configured, so we render the result as pretty json")
                card_context = {"result": result}
                card_template = 'ndr_core/result_renderers/default_template.html'
                html_string += get_template(card_template).render(card_context)

        return mark_safe(html_string)


@register.filter
def pretty_json(value):
    """Pretty prints a json string."""
    pretty_json_str = json.dumps(value, indent=4)
    pretty_json_str = pretty_json_str.replace('\n', '<br>').replace(' ', '&nbsp;')
    pretty_json_str = re.sub(
        r"https?://((www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}|localhost)"
        r"(:[0-9]{2,4})?\b([-a-zA-Z0-9()@:%_+.~#?&/=,]*)",
        lambda x: f'<a href="{x.group(0)}">{x.group(0)}</a>',
        pretty_json_str)

    return mark_safe(pretty_json_str)


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
    return isinstance(value, list)


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
    if isinstance(image_url, str):
        return ''
    if target_percent_of_size is None:
        return image_url

    if '/full/full/' in image_url:
        return image_url.replace('/full/full/', f'/full/pct:{target_percent_of_size}/')
    match = re.match(r'^.*/(\d*,\d*,\d*,\d*)/(full)/.*$', image_url)
    if match:
        return image_url.replace(match.group(2), f'pct:{target_percent_of_size}')


@register.filter
def translate_dict_value(key_to_translate, dict_name):
    """Translates 'value' value in a dictionary."""
    return translate_dict_foo(key_to_translate, dict_name, 'value')


@register.filter
def translate_dict_info(key_to_translate, dict_name):
    """Translates 'info' value in a dictionary."""
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
                if target_key in value_object:
                    return value_object[target_key]
                return f'{key_to_translate} (DNF)'
            if selected_language in additional_languages:
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
