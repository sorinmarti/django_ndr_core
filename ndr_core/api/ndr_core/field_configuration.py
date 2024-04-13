from ndr_core.models import NdrCoreSearchField


class FieldConfiguration:
    """A class to represent a field configuration. An API implementation can access a list of field configurations
    to create a query. """

    field = None
    """The field configuration."""

    value = None
    """The curated value of the field."""

    user_condition = None
    """The user defined condition of a list field. (and/or)"""

    def __init__(self, field_name, value):
        """Loads the corresponding field configuration from the search configuration and sets the value
        with al its manipulations.

        :param field_name: The name of the field.
        :param value: The value of the field."""
        try:
            self.field = NdrCoreSearchField.objects.get(field_name=field_name)
            self.set_value(value)
        except NdrCoreSearchField.DoesNotExist:
            raise ValueError(f"Field {field_name} does not exist.")

    def set_value(self, value):
        """Sets the value of the field and applies the specified type.

        :param value: The value of the field."""

        # A Multi list field returns a list of values
        if self.field.field_type == NdrCoreSearchField.FieldType.MULTI_LIST:
            edited_values = []
            for val in value:
                split = val.split('__')
                if len(split) == 2:
                    edited_val = split[0]
                else:
                    edited_val = val
                edited_values.append(self.apply_modifications(edited_val))
            self.value = edited_values
        # A boolean list field returns a list of tuples with the key and the boolean value to search for
        elif self.field.field_type == NdrCoreSearchField.FieldType.BOOLEAN_LIST:
            edited_values = []
            for val in value:
                split = val.split('__')
                if len(split) == 2:
                    edited_val = (split[0], True if split[1] == 'true' else False)
                else:
                    edited_val = (val, True)
                edited_values.append(edited_val)
            self.value = edited_values
        # A list field returns a single value
        elif self.field.field_type == NdrCoreSearchField.FieldType.LIST:
            split = value.split('__')
            if len(split) == 2:
                self.value = self.apply_modifications(split[0])
            else:
                self.value = self.apply_modifications(value)
        # A number field returns a single value
        elif self.field.field_type == NdrCoreSearchField.FieldType.NUMBER:
            self.value = self.apply_modifications(value)
        # A number range field returns a list of values
        elif self.field.field_type == NdrCoreSearchField.FieldType.NUMBER_RANGE:
            self.value = self.apply_modifications(value)
        # All other fields return a single value
        else:
            self.value = self.apply_modifications(value)

    def apply_modifications(self, value):
        # Apply the specified input transformation

        if self.field.data_field_type == "int":
            return int(value)
        elif self.field.data_field_type == "string":
            # If the value should be transformed by regex
            if self.field.input_transformation_regex is not None and self.field.input_transformation_regex != '' and '{_value_}' in self.field.input_transformation_regex:
                if isinstance(value, list):
                    print("islist: ", value)
                    value = "(" + '|'.join(map(str, value)) + ")"
                value = self.field.input_transformation_regex.replace('{_value_}', value)
            return str(value)
        return value


    @property
    def parameter(self):
        if self.field.api_parameter is None or self.field.api_parameter == '':
            return self.field.field_name
        return self.field.api_parameter

    @property
    def condition(self):
        if self.user_condition is not None:
            return self.user_condition.lower()
        return self.field.list_condition.lower()

    @property
    def field_type(self):
        if self.field.field_type == NdrCoreSearchField.FieldType.STRING:
            return 'string'
        elif self.field.field_type == NdrCoreSearchField.FieldType.NUMBER:
            return 'number'
        elif self.field.field_type == NdrCoreSearchField.FieldType.LIST:
            return 'list'
        elif self.field.field_type == NdrCoreSearchField.FieldType.MULTI_LIST:
            return 'multi_list'
        elif self.field.field_type == NdrCoreSearchField.FieldType.BOOLEAN_LIST:
            return 'boolean_list'
        elif self.field.field_type == NdrCoreSearchField.FieldType.NUMBER_RANGE:
            return 'number_range'
        elif self.field.field_type == NdrCoreSearchField.FieldType.DATE:
            return 'date'
        elif self.field.field_type == NdrCoreSearchField.FieldType.DATE_RANGE:
            return 'date_range'
        elif self.field.field_type == NdrCoreSearchField.FieldType.BOOLEAN:
            return 'boolean'
        return 'string'

