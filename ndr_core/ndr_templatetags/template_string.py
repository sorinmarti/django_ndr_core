"""Module for the TemplateString class."""
import json
import re
from string import Formatter

from django.utils.safestring import mark_safe

from ndr_core.ndr_templatetags.filters import get_get_filter_class


class TemplateStringVariable:
    """ A class to represent a template string variable. A variable is a string formatted in the NDR Core template
    language. It represents a value in the data dictionary. A variable can have filters, marked with
    pipes. Each filter can have options after a double pint (':'). The options can be separated with commas (',')
    and they can have values, separated with an equal sign ('='). Nested variables are separated with a dot ('.') or
    with square brackets ('[]').

        Examples: {test_value|upper}                                          Returns the test value in UPPER case.
                  {nested_data.nested_value|lower}                            Returns the nested value in lower case.
                  {nested_data[nested_value]lower}                            Returns the nested value in lower case.
                  {list_variable|upper}                                       Returns string representing a list where
                                                                                each value is in UPPER case.
                  {test_value|badge:color=red}                                Returns the test value as a bootstrap
                                                                                badge with the color red.
                  {test_value|bool:True-value,False-value}                    Converts a boolean value to with the
                                                                                given options.

        Format: {variable|filter1[:option[=value]|filter2|filter3]}         (The brackets show optional parts.)
    """

    LIST_SEPARATOR = ", "
    """ If the result is a list, the items are joined with this separator. """

    variable = ""
    """ The variable name without any filters or options. """

    raw_variable = ""
    """ The variable name with filters and options. """

    keys = []
    """ The list of keys the variable is composed of. If it is a nested variable, the keys are separated with a dot
    ('.') or with square brackets ('[]'). """

    value_filters = []
    """ A list of filters. """

    filter_configurations = []

    def __init__(self, variable):
        """Initializes the TemplateStringVariable class.
        Parses the variable and extracts the variable name, the filters and the options.
        Raises a ValueError if the variable is malformed."""

        self.raw_variable = variable
        self.parse_variable(variable)
        self.keys = self.get_keys()

    def parse_variable(self, variable):
        """Parses the variable and extracts the variable name, the filters and the options."""
        if variable is None:
            raise ValueError("Variable is None.")

        if '|' in variable:
            parts = variable.split('|')
            self.variable = parts[0]
            self.value_filters = parts[1:]

            self.filter_configurations = []
            for i, my_filter in enumerate(self.value_filters):
                p = my_filter.split(':')
                self.value_filters[i] = p[0]
                self.filter_configurations.append({})
                if len(p) > 1:
                    configs = p[1].split(',')
                    for cn, config in enumerate(configs):
                        if '=' in config:
                            k, v = config.split('=')
                            self.filter_configurations[i][k] = v
                        else:
                            self.filter_configurations[i][f"o{cn}"] = config
        else:
            self.variable = variable

    def get_raw_value(self, data):
        """Returns the value of the variable."""
        if self.is_nested():
            return self._get_nested_value(data)

        try:
            return data[self.variable]
        except KeyError as e:
            raise KeyError(f"Key not found in data: {e}") from e

    def get_value(self, data):
        """Returns the value of the variable with the filter applied."""
        try:
            raw_value = self.get_raw_value(data)
            if len(self.value_filters) > 0:
                if isinstance(raw_value, list):
                    filtered_values = []
                    for value in raw_value:
                        applied = self.apply_filters(value)
                        if applied is not None:
                            filtered_values.append(applied)
                    return filtered_values
                return self.apply_filters(self.get_raw_value(data))
            return raw_value
        except IndexError as e:
            raise IndexError(f"Key not found in list: {e}") from e
        except KeyError as e:
            raise KeyError(f"Key not found in data: {e}") from e
        except ValueError as e:
            raise ValueError(f"Could not parse variable: {e}") from e

    def _get_nested_value(self, data):
        """Returns the value of the variable."""
        keys = self.get_keys()
        value = data
        for key in keys:
            try:
                value = value[key]
            except TypeError as e:
                if key.isdigit():
                    try:
                        value = value[int(key)]
                    except IndexError:
                        raise IndexError(f"Nested key not found: {e}") from e
            except KeyError as e:
                raise KeyError(f"Nested key not found: {e}") from e
        return value

    def apply_filters(self, value):
        """Returns the value of the variable with the filter applied."""
        for i, my_filter in enumerate(self.value_filters):
            filter_class = get_get_filter_class(my_filter)
            if filter_class is None:
                raise ValueError(f"Filter {my_filter} not found.")
            value = filter_class(my_filter, value, self.filter_configurations[i]).get_rendered_value()

        return value

    def is_nested(self):
        """Returns True if the variable is nested."""
        return len(self.keys) > 1

    def get_keys(self):
        """Returns all nested keys in a key-string."""
        if re.match(r"^(\w+)(\[\w+?\])+$", self.variable):
            return self.get_keys_from_bracket_string()
        if re.match(r"^(\w+)(\.\w+)+$", self.variable):
            return self.get_keys_from_dot_string()
        if re.match(r"^(\w+)$", self.variable):
            return [self.variable]

        raise ValueError(f"Could not parse variable: {self.variable}")

    def get_keys_from_dot_string(self):
        """Returns all keys in a string."""
        return self.variable.split('.')

    def get_keys_from_bracket_string(self):
        """Returns all keys in a string."""
        match = re.findall(r"(.*?)\[(.*?)\]", self.variable)
        if match:
            match_path = []
            for match_item in match:
                for sub_match in match_item:
                    if sub_match != '':
                        match_path.append(sub_match)
            return match_path

        raise ValueError(f"Could not parse variable: {self.variable}")


class TemplateString:
    """ A class to represent a template string. A template string is a string formatted in the NDR COre template
    language. It is derived from the python format-string functionality. A string can have variables, marked with
     curly brackets. """

    show_errors = False
    string = ""
    data = {}
    variables = []

    def __init__(self, string, data, show_errors=False):
        self.string = string
        self.data = data
        self.variables = self.get_variables()
        self.show_errors = show_errors

    def get_variables(self, flatten=False):
        """Returns all variables in a string."""
        try:
            variables = []
            for var in Formatter().parse(self.string):
                if var[1] is not None and var[1] != '':
                    raw_variable_string = var[1]
                    if var[2] is not None and var[2] != '':
                        raw_variable_string += ':' + var[2]
                    variable = TemplateStringVariable(raw_variable_string)
                    variables.append(variable)

            if flatten:
                flat_variables = []
                for variable in variables:
                    flat_variables.append(variable.variable)
                return flat_variables
            return variables
        except ValueError as e:
            raise ValueError(f"Could not parse string: {e}") from e

    def get_string(self):
        """Returns the string.
        Example: "I want to see the {test_value}"
        """
        return self.string

    def get_formatted_string(self):
        """Returns the formatted string. All variables are replaced with their values. All filters are applied.
        Example: "I want to see the {key|upper}" -> "I want to see the CAT"""
        formatted_string = self.string
        for variable in self.variables:
            try:
                data = variable.get_value(self.data)
                if isinstance(data, list):
                    data = self.join_list(variable, data)
                formatted_string = formatted_string.replace(f"{{{variable.raw_variable}}}", str(data))
            except IndexError as e:
                formatted_string = formatted_string.replace(f"{{{variable.raw_variable}}}", self.get_error(e))
            except KeyError as e:
                formatted_string = formatted_string.replace(f"{{{variable.raw_variable}}}", self.get_error(e))
            except ValueError as e:
                formatted_string = formatted_string.replace(f"{{{variable.raw_variable}}}", self.get_error(e))

        return mark_safe(formatted_string)

    @staticmethod
    def join_list(variable, data):
        """Joins a list to a string using the LIST_SEPARATOR. The list items
        are converted to strings."""
        safe_data = []
        for item in data:
            if isinstance(item, dict):
                safe_data.append(json.dumps(item))
            else:
                safe_data.append(str(item))

        if len(safe_data) > 1:
            separator = variable.LIST_SEPARATOR
            return separator.join(safe_data)
        if len(safe_data) == 1:
            return safe_data[0]

        return ''

    def get_error(self, e):
        """Returns an error message to display within the result HTML."""
        if self.show_errors:
            alert = f'''<div class="alert alert-danger" role="alert">
                      {e}
                    </div>'''
            return mark_safe(alert)
        return ''

    def sanitize_html(self, field_content):
        """Removes empty elements from the html."""
        # return field_content
        pattern = r"<(\w+)>(&nbsp;)?</\1>"
        empty_element_match = re.findall(pattern, field_content)
        i = 0
        while empty_element_match:
            i = i + 1
            for match in empty_element_match:
                field_content = field_content.replace(f"<{match[0]}>{match[1]}</{match[0]}>", '')
            empty_element_match = re.findall(pattern, field_content)

        return mark_safe(field_content)
