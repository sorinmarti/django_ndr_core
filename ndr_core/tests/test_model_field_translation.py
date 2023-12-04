"""Tests for translations."""
from django.test import TestCase
from django.utils.translation import activate

from ndr_core.models import NdrCoreSearchField, NdrCoreTranslation
from ndr_core.tests.data import TEST_DATA, LIST_CHOICES


class ModelFieldTranslationTestCase(TestCase):
    """A class to test the ModelFieldTranslation class."""

    test_data = TEST_DATA

    def setUp(self):
        NdrCoreSearchField.objects.create(
            field_name='tags',
            field_label='Tags',
            field_type=NdrCoreSearchField.FieldType.LIST,
            field_required=False,
            help_text='Tags are cool',
            api_parameter='tags.tags',
            list_choices=LIST_CHOICES)
        NdrCoreTranslation.objects.create(
            language='de',
            table_name='ndrcoresearchfield',
            object_id='tags',
            field_name='field_label',
            translation='Schlagwörter')
        NdrCoreTranslation.objects.create(
            language='de',
            table_name='ndrcoresearchfield',
            object_id='tags',
            field_name='help_text',
            translation='Schlagwörter sind cool')

    def test_search_field_translation(self):
        """Tests the translation of a search field."""
        search_field = NdrCoreSearchField.objects.get(field_name='tags')
        activate('en')
        self.assertEqual(search_field.field_label, "Tags")
        self.assertEqual(search_field.help_text, "Tags are cool")
        activate('de')
        self.assertEqual(search_field.field_label, "Schlagwörter")
        self.assertEqual(search_field.help_text, "Schlagwörter sind cool")
