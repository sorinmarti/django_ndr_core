import json
from abc import ABC, abstractmethod

from django.utils.translation import get_language

from ndr_core.models import NdrCoreSearchField
from ndr_core.ndr_templatetags.filter_mixins import ColorOptionMixin


def get_get_filter_class(filter_name):
    """Returns the filter class."""
    if filter_name in ['lower', 'upper', 'title', 'capitalize']:
        return StringFilter
    if filter_name == 'bool':
        return BoolFilter
    if filter_name == 'fieldify':
        return FieldTemplateFilter
    elif filter_name in ['badge', 'pill']:
        return PillTemplateFilter
    elif filter_name == 'img':
        return ImageTemplateFilter
    else:
        return None


class AbstractFilter(ABC):
    """ A class to represent a filter. """

    filter_name = ""
    value = ""
    filter_configurations = {}

    def __init__(self, filter_name, value, filter_configurations):
        self.filter_name = filter_name
        self.value = value
        self.filter_configurations = filter_configurations

    @abstractmethod
    def get_rendered_value(self):
        pass

    def get_value(self):
        """Returns the formatted string."""
        print(self.filter_configurations)
        return self.value

    def get_configuration(self, name):
        try:
            value = self.filter_configurations[name]
        except KeyError:
            return None
        except AttributeError:
            return None
        return value


class StringFilter(AbstractFilter):
    """ A class to represent a template filter. """

    def __init__(self, filter_name, value, filter_configurations):
        super().__init__(filter_name, value, filter_configurations)

    def get_rendered_value(self):
        """Returns the formatted string."""
        if self.filter_name == 'upper':
            return self.get_value().upper()
        elif self.filter_name == 'lower':
            return self.get_value().lower()
        elif self.filter_name == 'title':
            return self.get_value().title()
        elif self.filter_name == 'capitalize':
            return self.get_value().capitalize()

        return self.get_value()


class BoolFilter(AbstractFilter):

    def get_rendered_value(self):
        print(self.filter_configurations, self.value, type(self.value))
        true_value = "True"
        if self.get_configuration('o0'):
            true_value = self.get_configuration('o0')
        false_value = "False"
        if self.get_configuration('o1'):
            false_value = self.get_configuration('o1')

        if isinstance(self.value, bool):
            if self.value:
                return self.replace_key_values(true_value)
            else:
                return self.replace_key_values(false_value)

        if isinstance(self.value, str):
            if self.value.lower() == 'true':
                return self.replace_key_values(true_value)
            else:
                return self.replace_key_values(false_value)

        return self.get_value()

    @staticmethod
    def replace_key_values(value):
        """ Replaces a value if it is a key value"""
        if value == '__none__':
            return ''
        return value


class FieldTemplateFilter(AbstractFilter):
    """ A class to represent a template filter. """

    field_value = ""
    search_field = None

    def __init__(self, filter_name, value, filter_configurations):
        super().__init__(filter_name, value, filter_configurations)
        try:
            self.search_field = NdrCoreSearchField.objects.get(field_name=self.get_configuration('field'))
            try:
                self.field_value = self.search_field.get_list_choices_as_dict()[self.value][self.get_language_value_field_name()]
            except KeyError:
                self.field_value = self.value

        except NdrCoreSearchField.DoesNotExist:
            self.search_field = None

    @staticmethod
    def get_language_value_field_name():
        """Returns the language value field name."""
        value_field_name = 'value'
        language = get_language()
        if language != 'en':
            value_field_name = f'value_{language}'
        return value_field_name

    def get_value(self):
        """Returns the formatted string."""
        return self.value

    def get_rendered_value(self):
        """Returns the formatted string."""
        if not self.search_field:
            return self.get_value()

        return self.field_value


class PillTemplateFilter(AbstractFilter, ColorOptionMixin):
    """ A class to represent a template filter. """

    template = ""

    def __init__(self, filter_name, value, filter_configurations):
        super().__init__(filter_name, value, filter_configurations)

        color = self.get_color_string(self.get_configuration('color'), self.value, color_string='background-color')

        display_string = self.value
        if isinstance(self.value, dict):
            value_option = self.get_configuration('value')
            if value_option:
                try:
                    display_string = self.value[value_option]
                except KeyError:
                    display_string = "KEY_ERROR"
            else:
                display_string = json.dumps(self.value)

        self.template = f'''<span class="badge badge-primary text-dark font-weight-normal" style="{color}">{display_string}</span>'''
        if ' style=""' in self.template:
            self.template = self.template.replace(' style=""', '')

    def get_value(self):
        """Returns the formatted string."""
        return self.value

    def get_rendered_value(self):
        """Returns the formatted string."""
        return self.template


class ImageTemplateFilter(AbstractFilter):
    def get_rendered_value(self):
        url = self.value
        if 'iiif_resize' in self.filter_configurations:
            url = url.replace('/full/0/default.',
                              f'/pct:{self.filter_configurations["iiif_resize"]}/0/default.')

        return f'<img src="{url}" class="img-fluid" alt="Responsive image">'
