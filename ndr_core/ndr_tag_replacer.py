import re

from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, get_language

from ndr_core.models import NdrCoreSearchField


class NdrTagReplacer:
    """Replaces tags in a text."""

    tag_pattern = r'\[\[(.*?)\]\]'
    valid_tags = ["pill", ]
    language = None

    def __init__(self):
        self.language = get_language()

    def replace_tags(self, text):
        """Replaces tags in a text."""
        text = self.parse_string(text)
        return mark_safe(text)

    def parse_string(self, text):
        """Parses a string."""

        match = re.search(self.tag_pattern, text)
        while match:
            # We have a match: [[...]]
            parts = match.groups()[0].split('|')
            if parts[0] in self.valid_tags:
                tag_name = parts[0]
                if len(parts) == 1:
                    # We have a simple tag: [[tag]]
                    text = text.replace(match.group(), self.create_replacement(tag_name, _("No content provided.")))
                elif len(parts) == 2:
                    # We have a tag with content: [[tag|content]]
                    text = text.replace(match.group(), self.create_replacement(tag_name, parts[1]))
                elif len(parts) == 3:
                    options = parts[2].split(',')
                    options_json = {}
                    for option in options:
                        o_tuple = option.split('=')
                        options_json[o_tuple[0]] = o_tuple[1]
                    # We have a tag with content and options: [[tag|content|field=field_name]]
                    text = text.replace(match.group(), self.create_replacement(tag_name, parts[1], options_json))
                pass
            match = re.search(self.tag_pattern, text)
        return text

    def create_replacement(self, tag_name, content, options={}):
        field = None
        color_string = ''

        if 'color' in options:
            if options['color'] == 'by_value':
                color_string = f' background-color: {self.translate_to_color(content, lightness=30)};'
            else:
                color_string = f' background-color: {options["color"]};'
        if 'field' in options:
            field = self.get_field(options['field'])
        if 'if' in options:
            if content == options['if'] and 'then' in options:
                content = options['then']
            elif 'else' in options:
                if options['else'] == 'None':
                    return ''
                else:
                    content = options['else']

        if tag_name == 'pill':
            return self.create_pill(content, field, color_string)

        return content

    def get_field(self, field_name):
        try:
            field = NdrCoreSearchField.objects.get(field_name=field_name)
            return field
        except NdrCoreSearchField.DoesNotExist:
            return None

    def translate_to_color(self, value, lightness=50):
        """Translates a value to a color."""
        if value is None:
            return ''

        hash_value = 0
        for char in value:
            hash_value = ord(char) + ((hash_value << 5) - hash_value)
            hash_value = hash_value & hash_value

        return f'hsl({hash_value % 360}, {100}%, {lightness}%)'

    def reduce_iiif_size(self, image_url, target_percent_of_size):
        """Reduces the size of an IIIF image URL."""
        if image_url is None:
            return ''
        if target_percent_of_size is None:
            return image_url

        if '/full/full/' in image_url:
            return image_url.replace('/full/full/', f'/full/pct:{target_percent_of_size}/')
        match = re.match(r'^.*/(\d*,\d*,\d*,\d*)/(full)/.*$', image_url)
        if match:
            print("Match found")
            return image_url.replace(match.group(2), f'pct:{target_percent_of_size}')

    def create_pill(self, content, field=None, color_string=''):
        if field is None:
            return (f'<span class="badge badge-secondary small" style="font-weight: normal;{color_string}">'
                    f'{content}'
                    '</span>')

        list_choices = field.get_list_choices_as_dict()
        if content in list_choices:
            obj_to_display = list_choices[content]
            if f"value_{self.language}" in obj_to_display:
                value = obj_to_display[f"value_{self.language}"]
            elif "value" in obj_to_display:
                value = obj_to_display["value"]
            else:
                value = content
            return (f'<span class="badge badge-secondary small" style="font-weight: normal;{color_string}">'
                    f'{value}'
                    '</span>')

        return (f'<span class="badge badge-secondary small" style="font-weight: normal;{color_string}">'
                f'{content}'
                '</span>')










