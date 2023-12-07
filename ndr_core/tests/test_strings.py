""" This module contains the tests for the ndr_core app. """
from django.test import TestCase

from ndr_core.ndr_templatetags.template_string import TemplateString
from ndr_core.tests.data import TEST_DATA


class TemplateStringTestCase(TestCase):
    """A class to test the TemplateString class."""

    test_data = TEST_DATA

    def test_simple_variable(self):
        """Tests a simple variable."""
        string = TemplateString("<p>I want to see the {test_value}</p>", self.test_data)
        self.assertEqual(string.get_variables(flatten=True), ['test_value'])
        self.assertEqual(string.variables[0].keys, ['test_value'])
        self.assertEqual(string.variables[0].is_nested(), False)
        self.assertEqual(string.variables[0].get_value(self.test_data), 'cat')
        self.assertEqual(string.get_formatted_string(), "<p>I want to see the cat</p>")

    def test_simple_variable_with_filters(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {test_value|upper}", self.test_data)
        self.assertEqual(string.get_variables(flatten=True), ['test_value'])
        self.assertEqual(string.variables[0].keys, ['test_value'])
        self.assertEqual(string.variables[0].is_nested(), False)
        self.assertEqual(string.variables[0].get_value(self.test_data), 'CAT')
        self.assertEqual(string.get_formatted_string(), "I want to see the CAT")

    def test_simple_variable_with_configured_filters(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {test_value|pill:color=red}", self.test_data)
        self.assertEqual(string.get_variables(flatten=True), ['test_value'])
        self.assertEqual(string.variables[0].get_value(self.test_data),
                         '<span class="badge badge-primary" style="color: red;">cat</span>')
        self.assertEqual(
            string.get_formatted_string(),
            "I want to see the <span class=\"badge badge-primary\" style=\"color: red;\">cat</span>")

    def test_simple_variable_with_multiple_filters(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {test_value|upper|pill:color=red}", self.test_data)
        self.assertEqual(string.get_variables(flatten=True), ['test_value'])
        self.assertEqual(string.variables[0].get_value(self.test_data),
                         '<span class="badge badge-primary" style="color: red;">CAT</span>')
        self.assertEqual(
            string.get_formatted_string(),
            "I want to see the <span class=\"badge badge-primary\" style=\"color: red;\">CAT</span>")

    def test_nested_variable(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {nested_data.nested_value}", self.test_data)
        self.assertEqual(string.get_variables(flatten=True), ['nested_data.nested_value'])
        self.assertEqual(string.variables[0].keys, ['nested_data', 'nested_value'])
        self.assertEqual(string.variables[0].is_nested(), True)
        self.assertEqual(string.variables[0].get_value(self.test_data), 'lion')
        self.assertEqual(string.get_formatted_string(), "I want to see the lion")

        string = TemplateString("I want to see the {nested_data[nested_value]}", self.test_data)
        self.assertEqual(string.get_variables(flatten=True), ['nested_data[nested_value]'])
        self.assertEqual(string.variables[0].get_value(self.test_data), 'lion')
        self.assertEqual(string.get_formatted_string(), "I want to see the lion")

    def test_multiple_simple_variables(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {test_value} and the {test_list}", self.test_data)
        self.assertEqual(string.get_variables(flatten=True), ['test_value', 'test_list'])
        self.assertEqual(string.variables[0].keys, ['test_value'])
        self.assertEqual(string.variables[1].keys, ['test_list'])
        self.assertEqual(string.variables[0].is_nested(), False)
        self.assertEqual(string.variables[1].is_nested(), False)
        self.assertEqual(string.variables[0].get_value(self.test_data), 'cat')
        self.assertEqual(string.variables[1].get_value(self.test_data), ['fish', 'dog', 'guinea pig'])
        self.assertEqual(string.get_formatted_string(),
                         "I want to see the cat and the fish, dog, guinea pig")

    def test_multiple_simple_variables_with_filters(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {test_value|upper} and the {test_list|capitalize}", self.test_data)
        self.assertEqual(string.variables[0].get_value(self.test_data), 'CAT')
        self.assertEqual(string.variables[1].get_value(self.test_data), ['Fish', 'Dog', 'Guinea pig'])
        self.assertEqual(string.get_formatted_string(),
                         "I want to see the CAT and the Fish, Dog, Guinea pig")

    def test_multiple_simple_variables_with_configured_filters(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {test_value|pill:color=red} "
                                "and the {test_list|pill:color=blue}", self.test_data)
        self.assertEqual(string.variables[0].get_value(self.test_data),
                         '<span class="badge badge-primary" style="color: red;">cat</span>')
        self.assertEqual(string.variables[1].get_value(self.test_data),
                         ['<span class="badge badge-primary" style="color: blue;">fish</span>',
                          '<span class="badge badge-primary" style="color: blue;">dog</span>',
                          '<span class="badge badge-primary" style="color: blue;">guinea pig</span>'])
        self.assertEqual(string.get_formatted_string(),
                         "I want to see the "
                         "<span class=\"badge badge-primary\" style=\"color: red;\">cat</span> and the "
                         "<span class=\"badge badge-primary\" style=\"color: blue;\">fish</span>, "
                         "<span class=\"badge badge-primary\" style=\"color: blue;\">dog</span>, "
                         "<span class=\"badge badge-primary\" style=\"color: blue;\">guinea pig</span>")

    def test_multiple_nested_variables(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {nested_data.nested_value} and the {nested_data[nested_list]}",
                                self.test_data)
        self.assertEqual(string.get_variables(flatten=True), ['nested_data.nested_value',
                                                              'nested_data[nested_list]'])
        self.assertEqual(string.variables[0].keys, ['nested_data', 'nested_value'])
        self.assertEqual(string.variables[1].keys, ['nested_data', 'nested_list'])
        self.assertEqual(string.variables[0].is_nested(), True)
        self.assertEqual(string.variables[1].is_nested(), True)
        self.assertEqual(string.variables[0].get_value(self.test_data), 'lion')
        self.assertEqual(string.variables[1].get_value(self.test_data), ['gazelle', 'zebra', 'buffalo'])

    def test_dict_list_variable(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {another_test_list}", self.test_data)
        self.assertEqual(string.get_variables(flatten=True), ['another_test_list'])
        self.assertEqual(string.variables[0].keys, ['another_test_list'])
        self.assertEqual(string.variables[0].is_nested(), False)
        self.assertEqual(string.variables[0].get_value(self.test_data),
                         [{'key_1': 'value_1', 'key_2': 'value_2'},
                             {'key_1': 'value_1', 'key_2': 'value_2'},
                             {'key_1': 'value_1', 'key_2': 'value_2'}])
        self.assertEqual(string.get_formatted_string(),
                         'I want to see the {"key_1": "value_1", "key_2": "value_2"}, '
                         '{"key_1": "value_1", "key_2": "value_2"}, '
                         '{"key_1": "value_1", "key_2": "value_2"}')

    def test_dict_list_variable_with_filters(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {another_test_list|pill}", self.test_data)
        self.assertEqual(string.get_formatted_string(),
                         "I want to see the "
                         "<span class=\"badge badge-primary\">{\"key_1\": \"value_1\", \"key_2\": \"value_2\"}</span>, "
                         "<span class=\"badge badge-primary\">{\"key_1\": \"value_1\", \"key_2\": \"value_2\"}</span>, "
                         "<span class=\"badge badge-primary\">{\"key_1\": \"value_1\", \"key_2\": \"value_2\"}</span>")

        string = TemplateString("I want to see the {another_test_list|pill:value=key_1,color=val__key_2}",
                                self.test_data)
        self.assertEqual(
            string.get_formatted_string(),
            "I want to see the "
            "<span class=\"badge badge-primary\" style=\"color: value_2;\">value_1</span>, "
            "<span class=\"badge badge-primary\" style=\"color: value_2;\">value_1</span>, "
            "<span class=\"badge badge-primary\" style=\"color: value_2;\">value_1</span>")

        string = TemplateString("I want to see the {another_test_list|pill:value=key_1,color=byval__key_2}",
                                self.test_data)
        self.assertEqual(
            string.get_formatted_string(),
            "I want to see the "
            "<span class=\"badge badge-primary\" style=\"color: hsl(116, 100%, 50%);\">value_1</span>, "
            "<span class=\"badge badge-primary\" style=\"color: hsl(116, 100%, 50%);\">value_1</span>, "
            "<span class=\"badge badge-primary\" style=\"color: hsl(116, 100%, 50%);\">value_1</span>")

    def test_invalid_variable(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {invalid_variable}", self.test_data)
        self.assertEqual(string.get_variables(flatten=True), ['invalid_variable'])
        self.assertEqual(string.variables[0].keys, ['invalid_variable'])
        self.assertEqual(string.variables[0].is_nested(), False)
        self.assertEqual(string.variables[0].get_value(self.test_data), 'KEY_ERROR')
        self.assertEqual(string.get_formatted_string(), "I want to see the KEY_ERROR")

    def test_invalid_nested_variable(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {nested_data.invalid_variable}", self.test_data)
        self.assertEqual(string.get_variables(flatten=True), ['nested_data.invalid_variable'])
        self.assertEqual(string.variables[0].keys, ['nested_data', 'invalid_variable'])
        self.assertEqual(string.variables[0].is_nested(), True)
        self.assertEqual(string.variables[0].get_value(self.test_data), 'KEY_ERROR')

    def test_invalid_string(self):
        """Tests a simple variable."""
        string = TemplateString("I want to see the {nested_data.invalid_variable", self.test_data)
        self.assertEqual(string.get_variables(flatten=True), [])
        self.assertEqual(string.variables, [])
        self.assertEqual(string.get_formatted_string(), "I want to see the {nested_data.invalid_variable")
