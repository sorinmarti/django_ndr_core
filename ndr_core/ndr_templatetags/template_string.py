"""Module for the TemplateString class."""
import json
import re
from string import Formatter

import html
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
            # Use quote-respecting split for pipes to handle quoted parameter values with pipes
            parts = self._split_filter_with_quotes(variable, '|')
            self.variable = parts[0]
            self.value_filters = parts[1:]

            self.filter_configurations = []
            for i, my_filter in enumerate(self.value_filters):
                p = self._split_filter_with_quotes(my_filter, ':')
                self.value_filters[i] = p[0]
                self.filter_configurations.append({})
                if len(p) > 1:
                    configs = self._split_filter_with_quotes(p[1], ',')
                    for cn, config in enumerate(configs):
                        if '=' in config:
                            k, v = config.split('=', 1)  # Split only on first =
                            # Remove quotes if present
                            v = self._remove_quotes(v)
                            self.filter_configurations[i][k] = v
                        else:
                            config = self._remove_quotes(config)
                            self.filter_configurations[i][f"o{cn}"] = config
        else:
            self.variable = variable


    def _split_filter_with_quotes(self, text, delimiter):
        """Split text by delimiter, respecting quoted strings and [...] bracket groups."""
        parts = []
        current_part = ""
        in_quotes = False
        quote_char = None
        bracket_depth = 0
        i = 0

        while i < len(text):
            char = text[i]

            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_part += char
            elif char == quote_char and in_quotes:
                # Check if it's escaped
                if i > 0 and text[i - 1] == '\\':
                    current_part += char
                else:
                    in_quotes = False
                    quote_char = None
                    current_part += char
            elif char == '[' and not in_quotes:
                bracket_depth += 1
                current_part += char
            elif char == ']' and not in_quotes:
                bracket_depth -= 1
                current_part += char
            elif char == delimiter and not in_quotes and bracket_depth == 0:
                if current_part.strip():
                    parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char

            i += 1

        if current_part.strip():
            parts.append(current_part.strip())

        return parts

    def _remove_quotes(self, text):
        """Remove surrounding quotes from text."""
        text = text.strip()
        if len(text) >= 2:
            if (text.startswith('"') and text.endswith('"')) or \
                    (text.startswith("'") and text.endswith("'")):
                return text[1:-1]
        return text

    def is_literal_string(self):
        """Returns True if the variable is a quoted literal string."""
        if not self.variable:
            return False
        variable = self.variable.strip()
        return (len(variable) >= 2 and
                ((variable.startswith('"') and variable.endswith('"')) or
                 (variable.startswith("'") and variable.endswith("'"))))

    @property
    def literal_value(self):
        """Returns the unquoted literal value if this is a literal string."""
        if self.is_literal_string():
            return self._remove_quotes(self.variable)
        return None

    def get_raw_value(self, data):
        """Returns the value of the variable."""
        # Handle literal strings first
        if self.is_literal_string():
            return self.literal_value

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
                    # Check if any filter wants to process the list as a whole
                    if self.any_filter_processes_list_as_whole():
                        return self.apply_filters(raw_value, data)
                    # Check for limit parameter in any filter configuration
                    limit = self.get_limit_from_filters()
                    if limit:
                        raw_value = raw_value[:limit]
                    filtered_values = []
                    for value in raw_value:
                        applied = self.apply_filters(value, data)
                        if applied is not None:
                            filtered_values.append(applied)
                    return filtered_values
                return self.apply_filters(self.get_raw_value(data), data)
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
            if value is None:
                return None
            try:
                if isinstance(value, list) and not key.isdigit():
                    # Collect sub-key from each dict in the list
                    value = [item[key] for item in value if isinstance(item, dict) and key in item]
                else:
                    value = value[key]
            except TypeError as e:
                if key.isdigit():
                    try:
                        value = value[int(key)]
                    except (IndexError, TypeError):
                        return None
                else:
                    return None
            except KeyError as e:
                raise KeyError(f"Nested key not found: {e}") from e
        return value

    def get_limit_from_filters(self):
        """Check if any filter has a limit parameter and return the first one found."""
        for filter_config in self.filter_configurations:
            if 'limit' in filter_config:
                try:
                    return int(filter_config['limit'])
                except (ValueError, TypeError):
                    continue
        return None

    def any_filter_processes_list_as_whole(self):
        """Check if any filter in the chain wants to process lists as a whole."""
        for i, my_filter in enumerate(self.value_filters):
            try:
                filter_class = get_get_filter_class(my_filter)
                if filter_class is None:
                    continue
                # Create a temporary instance to check the flag
                temp_instance = filter_class(my_filter, None, self.filter_configurations[i], None)
                if temp_instance.processes_list_as_whole():
                    return True
            except (ValueError, Exception):
                continue
        return False

    def apply_filters(self, value, data_context=None):
        """Returns the value of the variable with the filter applied."""
        for i, my_filter in enumerate(self.value_filters):
            filter_class = get_get_filter_class(my_filter)
            if filter_class is None:
                raise ValueError(f"Filter {my_filter} not found.")
            value = filter_class(my_filter, value, self.filter_configurations[i], data_context).get_rendered_value()

        return value

    def is_nested(self):
        """Returns True if the variable is nested."""
        # Literal strings are never nested
        if self.is_literal_string():
            return False
        return len(self.keys) > 1

    def get_keys(self):
        """Returns all nested keys in a key-string."""
        # Handle literal strings - they don't have keys in the data sense
        if self.is_literal_string():
            return [self.variable]

        # Allow dashes in variable names
        if re.match(r"^([\w-]+)(\[[\w-]+?\])+$", self.variable):
            return self.get_keys_from_bracket_string()
        if re.match(r"^([\w-]+)(\.[\w-]+)+$", self.variable):
            return self.get_keys_from_dot_string()
        if re.match(r"^([\w-]+)$", self.variable):
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
        """Initializes the TemplateString class.
        Parses the string and extracts the variables.
        Raises a ValueError if the string is malformed."""

        if string is not None:
            self.string = html.unescape(string)
        else:
            self.string = ""

        self.data = data
        self.variables = self.get_variables()
        self.show_errors = show_errors

    def get_variables(self, flatten=False):
        """Returns all variables in a string."""
        try:
            variables = []
            # Strip list block content so inner-template variables are not resolved
            # against the outer data context (they are handled by _process_list_blocks).
            string_for_parsing = re.sub(
                r'(?:<p[^>]*>\s*)?\[\[start_list=\w+\]\].*?\[\[end_list\]\](?:\s*</p>)?',
                '',
                self.string,
                flags=re.DOTALL
            )
            string_for_parsing = re.sub(
                r'(?:<p[^>]*>\s*)?\[\[start_info_box(?:=\w+)?\]\].*?\[\[end_info_box\]\](?:\s*</p>)?',
                '',
                string_for_parsing,
                flags=re.DOTALL
            )
            for var in Formatter().parse(string_for_parsing):
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

    @staticmethod
    def _strip_html_whitespace(text):
        """Strip leading/trailing <br>, &nbsp;, non-breaking spaces, and whitespace."""
        noise = r'(\s|<br\s*/?>|&nbsp;|\xa0)+'
        text = re.sub(r'^' + noise, '', text, flags=re.IGNORECASE)
        text = re.sub(noise + r'$', '', text, flags=re.IGNORECASE)
        return text

    def _process_list_blocks(self, string):
        """Pre-process [[start_list=varname]]...[[end_list]] blocks.

        For each block, the named list is retrieved from self.data, and the inner
        template is rendered once per item (with the item dict as data context).
        Results are wrapped in <ul class="ndr-list-block"><li>...</li></ul>.
        [[item]] markers inside the block are stripped before rendering.

        Also consumes an optional surrounding <p>...</p> that CKEditor adds, since
        a <p> wrapping a <ul> is invalid HTML.
        """
        pattern = re.compile(
            r'(?:<p[^>]*>\s*)?\[\[start_list=(\w+)\]\](.*?)\[\[end_list\]\](?:\s*</p>)?',
            re.DOTALL
        )

        def render_block(match):
            varname = match.group(1)
            inner_template = match.group(2)

            # Remove [[item]] markers and any surrounding HTML whitespace/br noise
            inner_template = re.sub(r'\[\[item\]\](\s|&nbsp;|\xa0)*', '', inner_template, flags=re.IGNORECASE)
            inner_template = self._strip_html_whitespace(inner_template)

            try:
                items = self.data[varname]
            except (KeyError, TypeError):
                return self.get_error(KeyError(varname))

            if not isinstance(items, list):
                items = [items]

            lis = []
            for item in items:
                if not isinstance(item, dict):
                    item = {'value': item}
                rendered = TemplateString(inner_template, item, self.show_errors).get_formatted_string()
                lis.append(f'<li>{rendered}</li>')

            return '<ul class="ndr-list-block">' + ''.join(lis) + '</ul>'

        return pattern.sub(render_block, string)

    def _process_info_boxes(self, string):
        """Pre-process [[start_info_box[=type]]]...[[end_info_box]] blocks.

        Renders the inner content as a Bootstrap alert. The optional type parameter
        controls the alert style: info (default), warning, danger, success.

        Example:
            [[start_info_box]]          → alert-info
            [[start_info_box=warning]]  → alert-warning
            [[start_info_box=danger]]   → alert-danger
            [[start_info_box=success]]  → alert-success
        """
        pattern = re.compile(
            r'(?:<p[^>]*>\s*)?\[\[start_info_box(?:=(\w+))?\]\](.*?)\[\[end_info_box\]\](?:\s*</p>)?',
            re.DOTALL
        )

        alert_classes = {
            'info':    ('alert-info',    'fa-circle-info'),
            'warning': ('alert-warning', 'fa-triangle-exclamation'),
            'danger':  ('alert-danger',  'fa-circle-exclamation'),
            'error':   ('alert-danger',  'fa-circle-exclamation'),
            'success': ('alert-success', 'fa-circle-check'),
        }

        def render_box(match):
            box_type = (match.group(1) or 'info').lower()
            inner_content = self._strip_html_whitespace(match.group(2))

            alert_class, icon = alert_classes.get(box_type, alert_classes['info'])
            rendered = TemplateString(inner_content, self.data, self.show_errors).get_formatted_string()

            return (
                f'<div class="alert {alert_class}" role="alert">'
                f'<i class="fa-regular {icon}"></i> {rendered}'
                f'</div>'
            )

        return pattern.sub(render_box, string)

    def get_formatted_string(self):
        """Returns the formatted string. All variables are replaced with their values. All filters are applied.
        Example: "I want to see the {key|upper}" -> "I want to see the CAT"""
        formatted_string = self._process_list_blocks(self.string)
        formatted_string = self._process_info_boxes(formatted_string)
        for variable in self.variables:
            try:
                data = variable.get_value(self.data)
                if isinstance(data, list):
                    data = self.join_list(variable, data)
                formatted_string = formatted_string.replace(f"{{{variable.raw_variable}}}", str(data))
            except (IndexError, KeyError) as e:
                # Check if any filter has a default value
                default_value = self.get_default_value_from_variable(variable)
                if default_value is not None:
                    # If the fallback comes from a standalone |default: filter, return it raw
                    # (bypassing badge, linkify, etc.). If it's inline in another filter's
                    # config (e.g. badge:bg=red,default=n/a), apply the full filter chain.
                    has_default_filter = 'default' in variable.value_filters
                    if not has_default_filter and len(variable.value_filters) > 0:
                        try:
                            default_value = variable.apply_filters(default_value, self.data)
                        except Exception:
                            pass
                    formatted_string = formatted_string.replace(f"{{{variable.raw_variable}}}", str(default_value))
                else:
                    formatted_string = formatted_string.replace(f"{{{variable.raw_variable}}}", self.get_error(e))
            except ValueError as e:
                formatted_string = formatted_string.replace(f"{{{variable.raw_variable}}}", self.get_error(e))

        return mark_safe(formatted_string)

    def get_default_value_from_variable(self, variable):
        """Check if any filter in the variable has a default value configured."""
        for i, filter_config in enumerate(variable.filter_configurations):
            # Check for universal 'default' parameter
            if 'default' in filter_config:
                return filter_config['default']
            # Check for DefaultFilter's 'value' parameter
            if 'value' in filter_config:
                return filter_config['value']
            # Support shorthand default:value syntax (stored as positional o0)
            if (i < len(variable.value_filters)
                    and variable.value_filters[i] == 'default'
                    and 'o0' in filter_config):
                return filter_config['o0']
        return None

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
        """Removes empty elements from the html, but preserves structurally important table elements."""
        # return field_content
        # Elements that should NOT be removed even when empty (table structure elements)
        preserve_elements = {'td', 'th', 'tr', 'table', 'thead', 'tbody', 'tfoot'}

        pattern = r"<(\w+)>(&nbsp;)?</\1>"
        empty_element_match = re.findall(pattern, field_content)
        i = 0
        while empty_element_match:
            i = i + 1
            # Filter out preserved elements from matches to avoid infinite loop
            matches_to_process = [match for match in empty_element_match
                                  if match[0].lower() not in preserve_elements]

            if not matches_to_process:
                # Only preserved elements remain, stop processing
                break

            for match in matches_to_process:
                field_content = field_content.replace(f"<{match[0]}>{match[1]}</{match[0]}>", '')

            # Re-scan for more empty elements
            empty_element_match = re.findall(pattern, field_content)

        return mark_safe(field_content)
