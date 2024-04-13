from django.test import TestCase
from django.utils.translation import activate

from ndr_core.models import NdrCoreSearchField, NdrCoreValue


class NdrCoreSearchFieldTest(TestCase):
    def setUp(self):
        NdrCoreSearchField.objects.create(
            field_type=NdrCoreSearchField.FieldType.BOOLEAN_LIST,
            field_name='bool_field',
            list_choices='[{"key": "bool1", "value": "One", "value_de": "Eins", "initial": true},'
                         ' {"key": "bool2", "value": "Two", "value_de": "Zwei", "condition": false}]'
        )

        NdrCoreSearchField.objects.create(
            field_type=NdrCoreSearchField.FieldType.LIST,
            field_name='test_field',
            list_choices='[{"key": "key1", "value": "One", "displayable": true}, '
                         ' {"key": "key2", "value": "Two"}]'
        )

        NdrCoreSearchField.objects.create(
            field_type=NdrCoreSearchField.FieldType.MULTI_LIST,
            field_name='multi_list_field',
            list_choices='[{"key": "key1", "value": "One"}, '
                         ' {"key": "key2", "value": "Two"}]'
        )

        NdrCoreValue.objects.create(
            value_name='available_languages',
            value_label='de,fr',
            value_type=NdrCoreValue.ValueType.MULTI_LIST
        )

    def test_choices(self):
        # 'value' is used
        bool_field = NdrCoreSearchField.objects.get(field_name='bool_field')
        choices_en = bool_field.get_choices()
        self.assertEqual(choices_en, [('bool1__true', 'One'), ('bool2__false', 'Two')])

        # Translation: 'value_de' is used
        activate('de')
        choices_de = bool_field.get_choices()
        self.assertEqual(choices_de, [('bool1__true', 'Eins'), ('bool2__false', 'Zwei')])

        # No translation: 'value' is used
        activate('fr')
        choices_fr = bool_field.get_choices()
        (self.assertEqual(choices_fr, [('bool1__true', 'One'), ('bool2__false', 'Two')]))

    def test_choices_list_dict(self):
        bool_field = NdrCoreSearchField.objects.get(field_name='bool_field')
        choices = bool_field.get_choices_list_dict()
        self.assertEqual({
                            "bool1": {"key": "bool1", "value": "One", "value_de": "Eins", "condition": True, "initial": True, "is_searchable": True, "is_printable": True},
                            "bool2": {"key": "bool2", "value": "Two", "value_de": "Zwei", "condition": False, "initial": "", "is_searchable": True, "is_printable": True}}, choices)
