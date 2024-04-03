from abc import ABC, abstractmethod

from django.utils.translation import get_language


class AbstractFilter(ABC):
    """A class to represent a filter."""

    filter_name = ""
    value = ""
    filter_configurations = {}

    def __init__(self, filter_name, value, filter_configurations):
        self.filter_name = filter_name
        self.value = value
        self.filter_configurations = filter_configurations

        self.check_configuration()

    @abstractmethod
    def get_rendered_value(self):
        pass

    @abstractmethod
    def needed_attributes(self):
        return []

    @abstractmethod
    def allowed_attributes(self):
        return []

    @abstractmethod
    def needed_options(self):
        return []

    def check_configuration(self):
        for needed_option in self.needed_options():
            if not self.get_configuration(needed_option):
                raise ValueError(
                    f"Filter {self.filter_name} requires option {needed_option}."
                )
        for needed_attribute in self.needed_attributes():
            if not self.get_configuration(needed_attribute):
                raise ValueError(
                    f"Filter {self.filter_name} requires attribute {needed_attribute}."
                )
        for attribute in self.filter_configurations:
            if (
                attribute not in self.allowed_attributes()
                and attribute not in self.needed_attributes()
                and attribute not in self.needed_options()
            ):
                raise ValueError(
                    f"Filter {self.filter_name} does not allow attribute {attribute}."
                )

    def get_value(self):
        """Returns the formatted string."""
        return self.value

    def get_configuration(self, name):
        """Returns the configuration value."""
        try:
            value = self.filter_configurations[name]
        except KeyError:
            return None
        except AttributeError:
            return None
        return value

    @staticmethod
    def replace_key_values(value):
        """Replaces a value if it is a key value"""
        if value == "__none__":
            return ""
        return value

    @staticmethod
    def get_language_value_field_name():
        """Returns the language value field name."""
        value_field_name = "value"
        language = get_language()
        if language != "en":
            value_field_name = f"value_{language}"
        return value_field_name

    @staticmethod
    def get_language_info_field_name():
        """Returns the language value field name."""
        value_field_name = "info"
        language = get_language()
        if language != "en":
            value_field_name = f"info_{language}"
        return value_field_name
