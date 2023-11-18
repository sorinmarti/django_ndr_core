"""Contains forms used in the NDRCore admin interface to edit translations."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import (
    NdrCorePage,
    NdrCoreTranslation,
    NdrCoreSearchField,
    NdrCoreValue,
    NdrCoreSearchConfiguration, NdrCoreUIElement
)


class TranslateForm(forms.Form):
    """Base form to translate values. """

    lang = 'en'
    table_name = None
    items = None

    def __init__(self, *args, **kwargs):
        if 'lang' in kwargs:
            self.lang = kwargs.pop('lang')

        super().__init__(*args, **kwargs)

    @staticmethod
    def get_field(str_to_translate, help_text):
        """Returns a CharField with the given string as label. """
        field = forms.CharField(label=f"Translate: '{str_to_translate}'",
                                required=False,
                                max_length=100,
                                help_text=help_text)
        return field

    def get_initial_value(self, field_name, object_id):
        """Returns the initial value of the field. """
        try:
            translation_obj = NdrCoreTranslation.objects.get(language=self.lang,
                                                             table_name=self.table_name,
                                                             field_name=field_name,
                                                             object_id=object_id)
            return translation_obj.translation
        except NdrCoreTranslation.DoesNotExist:
            return ''

    def save_translation(self, object_id, field_name, translation):
        """Saves the translation to the database. """
        i18n_object = NdrCoreTranslation.objects.get_or_create(language=self.lang,
                                                               table_name=self.table_name,
                                                               field_name=field_name,
                                                               object_id=object_id)
        i18n_object[0].translation = translation
        i18n_object[0].save()


class TranslatePageForm(TranslateForm):
    """Form to translate page values """

    items = NdrCorePage.objects.all()
    table_name = 'NdrCorePage'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_values = {}
        for page in self.items:
            self.fields[f"page_title_{page.id}"] = self.get_field(page.name,
                                                                  "The page's Title")
            self.fields[f"nav_label_{page.id}"] = self.get_field(page.label,
                                                                 "The page's Navigation Label")

            initial_values[f"page_title_{page.id}"] = self.get_initial_value('name', str(page.id))
            initial_values[f"nav_label_{page.id}"] = self.get_initial_value('label', str(page.id))

        self.initial = initial_values

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for page in self.items:
            form_row = Row(
                Column(f"page_title_{page.id}", css_class='form-group col-6'),
                Column(f"nav_label_{page.id}", css_class='form-group col-6'),
                css_class='form-row'
            )
            layout.append(form_row)

        layout.append(get_form_buttons('Save Translations'))

        return helper

    def save_translations(self):
        """Saves the translations to the database. """
        self.is_valid()

        for page in self.items:
            self.save_translation(str(page.id), 'name', self.cleaned_data[f"page_title_{page.id}"])
            self.save_translation(str(page.id), 'label', self.cleaned_data[f"nav_label_{page.id}"])


class TranslateFieldForm(TranslateForm):
    """Form to translate form field values """

    items = NdrCoreSearchField.objects.all()
    table_name = 'NdrCoreSearchField'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_values = {}
        for field in self.items:
            self.fields[f"field_label_{field.field_name}"] = self.get_field(field.field_label,
                                                                            "The search field's Label")
            self.fields[f"field_help_text_{field.field_name}"] = self.get_field(field.help_text,
                                                                                "The search field's Help Text")

            initial_values[f"field_label_{field.field_name}"] = self.get_initial_value('field_label',
                                                                                       field.field_name)
            initial_values[f"field_help_text_{field.field_name}"] = self.get_initial_value('help_text',
                                                                                           field.field_name)

        self.initial = initial_values

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for field in self.items:
            form_row = Row(
                Column(f"field_label_{field.field_name}", css_class='form-group col-4'),
                Column(f"field_help_text_{field.field_name}", css_class='form-group col-8'),
                css_class='form-row'
            )
            layout.append(form_row)

        layout.append(get_form_buttons('Save Search Field Translations'))

        return helper

    def save_translations(self):
        """Saves the translations to the database. """
        self.is_valid()

        for field in self.items:
            self.save_translation(field.field_name,
                                  'field_label',
                                  self.cleaned_data[f"field_label_{field.field_name}"])
            self.save_translation(field.field_name,
                                  'help_text',
                                  self.cleaned_data[f"field_help_text_{field.field_name}"])


class TranslateSettingsForm(TranslateForm):
    """Form to translate settings values. """

    items = NdrCoreValue.objects.filter(value_type__in=[NdrCoreValue.ValueType.STRING,
                                                        NdrCoreValue.ValueType.URL],
                                        is_translatable=True)
    table_name = 'NdrCoreValue'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_values = {}
        for field in self.items:
            self.fields[f"setting_{field.value_name}"] = (
                self.get_field(field.value_value,
                               f"Value of the setting <b>{field.value_label}</b> "
                               f"(Help text: <i>{field.value_help_text}</i>)"))

            initial_values[f"setting_{field.value_name}"] = self.get_initial_value('value_value',
                                                                                   field.value_name)

        self.initial = initial_values

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for field in self.items:
            form_row = Row(
                Column(f"setting_{field.value_name}", css_class='form-group col-12'),
                css_class='form-row'
            )
            layout.append(form_row)

        layout.append(get_form_buttons('Save Settings Translations'))

        return helper

    def save_translations(self):
        """Saves the translations to the database. """
        self.is_valid()

        for field in self.items:
            self.save_translation(field.value_name, 'value_value',
                                  self.cleaned_data[f"setting_{field.value_name}"])


class TranslateFormForm(TranslateForm):
    """Form to translate settings values. """

    items = NdrCoreSearchConfiguration.objects.all()
    table_name = 'NdrCoreSearchConfiguration'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_values = {}
        for field in self.items:
            self.fields[f"setting_{field.conf_name}"] = (
                self.get_field(field.conf_label, f"Value of the configuration <b>{field.conf_name}</b></i>)"))

            initial_values[f"setting_{field.conf_name}"] = self.get_initial_value('conf_label',
                                                                                  field.conf_name)

        self.initial = initial_values

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for field in self.items:
            form_row = Row(
                Column(f"setting_{field.conf_name}", css_class='form-group col-12'),
                css_class='form-row'
            )
            layout.append(form_row)

        layout.append(get_form_buttons('Save Form Configuration Translations'))

        return helper

    def save_translations(self):
        """Saves the translations to the database. """
        self.is_valid()

        for field in self.items:
            self.save_translation(field.conf_name, 'conf_label', self.cleaned_data[f"setting_{field.conf_name}"])


class TranslateUIElementsForm(TranslateForm):
    """Form to translate settings values. """

    items = NdrCoreUIElement.objects.all()
    table_name = 'NdrCoreUIElement'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        initial_values = {}
        for field in self.items:
            if field.type == NdrCoreUIElement.UIElementType.CARD:
                pass
        self.initial = initial_values

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for field in self.items:
            """form_row = Row(
                Column(f"setting_{field.conf_name}", css_class='form-group col-12'),
                css_class='form-row'
            )
            layout.append(form_row)"""

        layout.append(get_form_buttons('Save UI Elements Translations'))

        return helper

    def save_translations(self):
        """Saves the translations to the database. """
        self.is_valid()

        for field in self.items:
            """i18n_object_settings = NdrCoreTranslation.objects.get_or_create(language=self.lang,
                                                                            table_name='NdrCoreSearchConfiguration',
                                                                            field_name='conf_label',
                                                                            object_id=field.conf_name)
            i18n_object_settings[0].translation = self.cleaned_data[f"setting_{field.conf_name}"]
            i18n_object_settings[0].save()"""


class TranslateImagesForm(TranslateForm):
    """Form to translate settings values. """

    ndr_image = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ndr_image = NdrCoreUIElement.objects.all()

        initial_values = {}
        for field in self.ndr_image:
            pass

        self.initial = initial_values

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for field in self.ndr_image:
            """form_row = Row(
                Column(f"setting_{field.conf_name}", css_class='form-group col-12'),
                css_class='form-row'
            )
            layout.append(form_row)"""

        layout.append(get_form_buttons('Save Images Translations'))

        return helper

    def save_translations(self):
        """Saves the translations to the database. """
        self.is_valid()

        for field in self.ndr_image:
            """i18n_object_settings = NdrCoreTranslation.objects.get_or_create(language=self.lang,
                                                                            table_name='NdrCoreSearchConfiguration',
                                                                            field_name='conf_label',
                                                                            object_id=field.conf_name)
            i18n_object_settings[0].translation = self.cleaned_data[f"setting_{field.conf_name}"]
            i18n_object_settings[0].save()"""
