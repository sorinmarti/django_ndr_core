import json
from abc import ABC, abstractmethod
from datetime import datetime

from django.utils.translation import get_language

from ndr_core.models import NdrCoreSearchField
from ndr_core.ndr_templatetags.abstract_filter import AbstractFilter
from ndr_core.ndr_templatetags.html_element import HTMLElement


def get_get_filter_class(filter_name):
    """Returns the filter class."""
    if filter_name in ["lower", "upper", "title", "capitalize"]:
        return StringFilter
    if filter_name == "bool":
        return BoolFilter
    if filter_name == "fieldify":
        return FieldTemplateFilter
    if filter_name in ["badge", "pill"]:
        return BadgeTemplateFilter
    if filter_name == "img":
        return ImageTemplateFilter
    if filter_name == "date":
        return DateFilter
    if filter_name == "format":
        return NumberFilter

    raise ValueError(f"Filter {filter_name} not found.")


class StringFilter(AbstractFilter):
    """A class to represent a template filter."""

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return []

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns the formatted string."""
        if self.filter_name == "upper":
            return self.get_value().upper()
        if self.filter_name == "lower":
            return self.get_value().lower()
        if self.filter_name == "title":
            return self.get_value().title()
        if self.filter_name == "capitalize":
            return self.get_value().capitalize()

        return self.get_value()


class BoolFilter(AbstractFilter):
    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return []

    def needed_options(self):
        return ["o0", "o1"]

    def get_rendered_value(self):
        true_value = "True"
        if self.get_configuration("o0"):
            true_value = self.get_configuration("o0")
        false_value = "False"
        if self.get_configuration("o1"):
            false_value = self.get_configuration("o1")

        if isinstance(self.value, bool):
            if self.value:
                return self.replace_key_values(true_value)
            return self.replace_key_values(false_value)

        if isinstance(self.value, str):
            if self.value.lower() == "true":
                return self.replace_key_values(true_value)
            return self.replace_key_values(false_value)

        return self.get_value()


class FieldTemplateFilter(AbstractFilter):
    """A class to represent a template filter."""

    field_value = ""
    search_field = None

    def __init__(self, filter_name, value, filter_configurations):
        super().__init__(filter_name, value, filter_configurations)
        try:
            self.search_field = NdrCoreSearchField.objects.get(
                field_name=self.get_configuration("o0")
            )
            try:
                self.field_value = self.search_field.get_list_choices_as_dict()[
                    self.value
                ][self.get_language_value_field_name()]
            except KeyError:
                self.field_value = self.value

        except NdrCoreSearchField.DoesNotExist:
            self.search_field = None

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return []

    def needed_options(self):
        return ["o0"]

    def get_rendered_value(self):
        """Returns the formatted string."""
        if not self.search_field:
            return self.get_value()

        return self.field_value


class BadgeTemplateFilter(AbstractFilter):
    """A class to represent a template filter."""

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["field", "color", "bg", "tt"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns the formatted string."""

        badge_element = HTMLElement("span")
        badge_element.add_attribute("class", "badge")
        badge_element.add_attribute("class", "text-dark")
        badge_element.add_attribute("class", "font-weight-normal")

        if self.get_configuration("tt"):
            badge_element.add_attribute("data-toggle", "tooltip")
            badge_element.add_attribute("data-placement", "top")

        field_options = None
        if self.get_configuration("field"):
            # The 'field' option is set. Try to get a translated value from the NDRCoreSearchField
            try:
                field = NdrCoreSearchField.objects.get(
                    field_name=self.get_configuration("field")
                )
                all_field_options = field.get_choices_list_dict()
                field_options = all_field_options[self.value]
                if not field_options['is_printable']:
                    return None

                badge_element.add_content(
                    field_options[self.get_language_value_field_name()]
                )
                if self.get_configuration("tt"):
                    tt_content = self.get_configuration("tt")
                    if tt_content == "__field__":
                        tt_text = field_options[self.get_language_info_field_name()]
                    else:
                        tt_text = tt_content
                    badge_element.add_attribute("title", tt_text)
            except NdrCoreSearchField.DoesNotExist:
                badge_element.add_content("Field not found")  # TODO: internationalize
        else:
            badge_element.add_content(self.value)

        if self.get_configuration("color"):
            badge_element.manage_color_attribute(
                "color", self.get_configuration("color"), self.value, field_options
            )
        if self.get_configuration("bg"):
            badge_element.manage_color_attribute(
                "bg", self.get_configuration("bg"), self.value, field_options
            )

        return str(badge_element)


class ImageTemplateFilter(AbstractFilter):
    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["iiif_resize"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        url = self.value

        if self.get_configuration("iiif_resize"):
            url = url.replace(
                "/full/0/default.",
                f'/pct:{self.filter_configurations["iiif_resize"]}/0/default.',
            )

        element = HTMLElement("img")
        element.add_attribute("src", url)
        element.add_attribute("class", "img-fluid")
        element.add_attribute("alt", "Responsive image")

        return str(element)


class DateFilter(AbstractFilter):
    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["format"]

    def needed_options(self):
        return ["o0"]

    def get_rendered_value(self):
        """Returns the formatted string."""
        common_formats = ["%Y-%m-%d"]
        if self.get_configuration("format"):
            common_formats = [self.get_configuration("format")]

        for d_format in common_formats:
            try:
                date_object = datetime.strptime(self.value, d_format)
                return date_object.strftime(self.get_configuration("o0"))
            except ValueError:
                pass

        return self.get_value()


class NumberFilter(AbstractFilter):
    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return []

    def needed_options(self):
        return ['o0']

    def get_rendered_value(self):
        """Returns the formatted string."""
        number_value = int(self.get_value())
        try:
            return ("{:" + self.get_configuration('o0') + "}").format(number_value)
        except ValueError:
            return self.get_value()

    def get_value(self):
        """Returns the formatted string."""
        return self.value
