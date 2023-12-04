"""A module to test the fieldify filter."""
from django.test import TestCase

from django.utils.translation import activate

from ndr_core.models import NdrCoreSearchField
from ndr_core.ndr_templatetags.template_string import TemplateString
from ndr_core.tests.data import TEST_DATA, LIST_CHOICES


class TemplateStringTestCase(TestCase):
    """A class to test the TemplateString class."""

    test_data = TEST_DATA

    def setUp(self):
        NdrCoreSearchField.objects.create(
            field_name='tags',
            field_label='Tags',
            field_type=NdrCoreSearchField.FieldType.LIST,
            field_required=False,
            help_text='Tags',
            api_parameter='tags.tags',
            list_choices=LIST_CHOICES)

    def test_translated_field_value(self):
        """Tests a simple variable with the field filter."""
        string = TemplateString("I want to see the {test_value|fieldify:field=tags}", self.test_data)
        activate('en')
        self.assertEqual(string.get_formatted_string(), "I want to see the Cat")
        activate('de')
        self.assertEqual(string.get_formatted_string(), "I want to see the Katze")

    def test_translated_field_value_list(self):
        """Tests a simple variable with the field filter."""
        string = TemplateString("I want to see the {test_list|fieldify:field=tags}", self.test_data)
        activate('en')
        self.assertEqual(string.get_formatted_string(), "I want to see the Fish, Dog, Guinea pig")
        activate('de')
        self.assertEqual(string.get_formatted_string(), "I want to see the Fisch, Hund, Meerschweinchen")

    def test_translated_field_value_nested(self):
        """Tests a simple variable with the field filter."""
        string = TemplateString("I want to see the {nested_data[nested_value]|fieldify:field=tags}", self.test_data)
        activate('en')
        self.assertEqual(string.get_formatted_string(), "I want to see the Lion")
        activate('de')
        self.assertEqual(string.get_formatted_string(), "I want to see the Löwe")

    def test_translated_field_value_nested_list(self):
        """Tests a simple variable with the field filter."""
        string = TemplateString("I want to see the {nested_data.nested_list|fieldify:field=tags}", self.test_data)
        activate('en')
        self.assertEqual(string.get_formatted_string(), "I want to see the Gazelle, Zebra, Buffalo")
        activate('de')
        self.assertEqual(string.get_formatted_string(), "I want to see the Gazelle, Zebra, Büffel")
