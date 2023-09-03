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
    NdrCoreSearchConfiguration
)


class TranslateForm(forms.Form):
    lang = 'en'

    def __init__(self, *args, **kwargs):
        if 'lang' in kwargs:
            self.lang = kwargs.pop('lang')

        super(TranslateForm, self).__init__(*args, **kwargs)


class TranslatePageForm(TranslateForm):
    """Form to translate page values """

    pages = None

    def __init__(self, *args, **kwargs):
        super(TranslatePageForm, self).__init__(*args, **kwargs)
        self.pages = NdrCorePage.objects.all()

        initial_values = {}
        for page in self.pages:
            self.fields[f"page_title_{page.id}"] = forms.CharField(label=f"Translate: '{page.name}'", required=False,
                                                                   max_length=100,
                                                                   help_text="The page's Title")
            self.fields[f"nav_label_{page.id}"] = forms.CharField(label=f"Translate: '{page.label}'", required=False,
                                                                  max_length=100,
                                                                  help_text="The page's Navigation Label")
            try:
                name = NdrCoreTranslation.objects.get(language=self.lang,
                                                      table_name='NdrCorePage',
                                                      field_name='name',
                                                      object_id=str(page.id))
                initial_values[f"page_title_{page.id}"] = name.translation
            except NdrCoreTranslation.DoesNotExist:
                pass

            try:
                label = NdrCoreTranslation.objects.get(language=self.lang,
                                                       table_name='NdrCorePage',
                                                       field_name='label',
                                                       object_id=str(page.id))
                initial_values[f"nav_label_{page.id}"] = label.translation
            except NdrCoreTranslation.DoesNotExist:
                pass

        self.initial = initial_values

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for page in self.pages:
            form_row = Row(
                Column(f"page_title_{page.id}", css_class='form-group col-md-6 mb-0'),
                Column(f"nav_label_{page.id}", css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            )
            layout.append(form_row)

        layout.append(get_form_buttons('Save Translations'))

        return helper

    def save_translations(self):
        """Saves the translations to the database. """
        self.is_valid()

        for page in self.pages:
            i18n_object_page_title = NdrCoreTranslation.objects.get_or_create(language=self.lang,
                                                                              table_name='NdrCorePage',
                                                                              field_name='name',
                                                                              object_id=str(page.id))
            i18n_object_page_title[0].translation = self.cleaned_data[f"page_title_{page.id}"]
            i18n_object_page_title[0].save()

            i18n_object_nav_label = NdrCoreTranslation.objects.get_or_create(language=self.lang,
                                                                             table_name='NdrCorePage',
                                                                             field_name='label',
                                                                             object_id=str(page.id))
            i18n_object_nav_label[0].translation = self.cleaned_data[f"nav_label_{page.id}"]
            i18n_object_nav_label[0].save()


class TranslateFieldForm(TranslateForm):
    """Form to translate form field values """

    ndr_form_fields = None

    def __init__(self, *args, **kwargs):
        super(TranslateFieldForm, self).__init__(*args, **kwargs)
        self.ndr_form_fields = NdrCoreSearchField.objects.all()

        initial_values = {}
        for field in self.ndr_form_fields:
            self.fields[f"field_label_{field.field_name}"] = forms.CharField(label=f"Translate: '{field.field_label}'",
                                                                             required=False,
                                                                             max_length=100,
                                                                             help_text="The search field's Label")
            self.fields[f"field_help_text_{field.field_name}"] = forms.CharField(label=f"Translate: '{field.help_text}'",
                                                                                 required=False,
                                                                                 max_length=100,
                                                                                 help_text="The search field's Help Text")
            try:
                field_label = NdrCoreTranslation.objects.get(language=self.lang,
                                                             table_name='NdrCoreSearchField',
                                                             field_name='field_label',
                                                             object_id=field.field_name)
                initial_values[f"field_label_{field.field_name}"] = field_label.translation
                # print(field_label.translation)
            except NdrCoreTranslation.DoesNotExist:
                pass

            try:
                label = NdrCoreTranslation.objects.get(language=self.lang,
                                                       table_name='NdrCoreSearchField',
                                                       field_name='help_text',
                                                       object_id=field.field_name)
                initial_values[f"field_help_text_{field.field_name}"] = label.translation
            except NdrCoreTranslation.DoesNotExist:
                pass

        self.initial = initial_values

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for field in self.ndr_form_fields:
            form_row = Row(
                Column(f"field_label_{field.field_name}", css_class='form-group col-md-4 mb-0'),
                Column(f"field_help_text_{field.field_name}", css_class='form-group col-md-8 mb-0'),
                css_class='form-row'
            )
            layout.append(form_row)

        layout.append(get_form_buttons('Save Search Field Translations'))

        return helper

    def save_translations(self):
        """Saves the translations to the database. """
        self.is_valid()

        for field in self.ndr_form_fields:
            i18n_object_field_label = NdrCoreTranslation.objects.get_or_create(language=self.lang,
                                                                               table_name='NdrCoreSearchField',
                                                                               field_name='field_label',
                                                                               object_id=field.field_name)
            i18n_object_field_label[0].translation = self.cleaned_data[f"field_label_{field.field_name}"]
            i18n_object_field_label[0].save()

            i18n_object_help_text = NdrCoreTranslation.objects.get_or_create(language=self.lang,
                                                                             table_name='NdrCoreSearchField',
                                                                             field_name='help_text',
                                                                             object_id=field.field_name)
            i18n_object_help_text[0].translation = self.cleaned_data[f"field_help_text_{field.field_name}"]
            i18n_object_help_text[0].save()


class TranslateSettingsForm(TranslateForm):
    """Form to translate settings values. """

    ndr_settings_fields = None

    def __init__(self, *args, **kwargs):
        super(TranslateSettingsForm, self).__init__(*args, **kwargs)
        self.ndr_settings_fields = NdrCoreValue.objects.filter(value_type__in=[NdrCoreValue.ValueType.STRING,
                                                                               NdrCoreValue.ValueType.URL],
                                                               is_translatable=True)

        initial_values = {}
        for field in self.ndr_settings_fields:
            self.fields[f"setting_{field.value_name}"] = forms.CharField(label=f"Translate: '{field.value_value}'",
                                                                         required=False,
                                                                         max_length=100,
                                                                         help_text=f"Value of the setting <b>{field.value_label}</b> (Help text: <i>{field.value_help_text}</i>)")
            try:
                field_label = NdrCoreTranslation.objects.get(language=self.lang,
                                                             table_name='NdrCoreValue',
                                                             field_name='value_value',
                                                             object_id=field.value_name)
                initial_values[f"setting_{field.value_name}"] = field_label.translation
            except NdrCoreTranslation.DoesNotExist:
                pass

        self.initial = initial_values

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for field in self.ndr_settings_fields:
            form_row = Row(
                Column(f"setting_{field.value_name}", css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            )
            layout.append(form_row)

        layout.append(get_form_buttons('Save Settings Translations'))

        return helper

    def save_translations(self):
        """Saves the translations to the database. """
        self.is_valid()

        for field in self.ndr_settings_fields:
            i18n_object_settings = NdrCoreTranslation.objects.get_or_create(language=self.lang,
                                                                            table_name='NdrCoreValue',
                                                                            field_name='value_value',
                                                                            object_id=field.value_name)
            i18n_object_settings[0].translation = self.cleaned_data[f"setting_{field.value_name}"]
            i18n_object_settings[0].save()


class TranslateFormForm(TranslateForm):
    """Form to translate settings values. """

    ndr_search_conf = None

    def __init__(self, *args, **kwargs):
        super(TranslateFormForm, self).__init__(*args, **kwargs)
        self.ndr_search_conf = NdrCoreSearchConfiguration.objects.all()

        initial_values = {}
        for field in self.ndr_search_conf:
            self.fields[f"setting_{field.conf_name}"] = forms.CharField(
                label=f"Translate: '{field.conf_label}'",
                required=False,
                max_length=100,
                help_text=f"Value of the configuration <b>{field.conf_name}</b></i>)")
            try:
                conf_label = NdrCoreTranslation.objects.get(language=self.lang,
                                                            table_name='NdrCoreSearchConfiguration',
                                                            field_name='conf_label',
                                                            object_id=field.conf_name)
                initial_values[f"setting_{field.conf_name}"] = conf_label.translation
            except NdrCoreTranslation.DoesNotExist:
                pass

        self.initial = initial_values

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for field in self.ndr_search_conf:
            form_row = Row(
                Column(f"setting_{field.conf_name}", css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            )
            layout.append(form_row)

        layout.append(get_form_buttons('Save Form Configuration Translations'))

        return helper

    def save_translations(self):
        """Saves the translations to the database. """
        self.is_valid()

        for field in self.ndr_search_conf:
            i18n_object_settings = NdrCoreTranslation.objects.get_or_create(language=self.lang,
                                                                            table_name='NdrCoreSearchConfiguration',
                                                                            field_name='conf_label',
                                                                            object_id=field.conf_name)
            i18n_object_settings[0].translation = self.cleaned_data[f"setting_{field.conf_name}"]
            i18n_object_settings[0].save()
