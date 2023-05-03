"""Forms used in the NDRCore admin interface for in-app settings."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, HTML
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreValue


class SettingsListForm(forms.Form):
    """Shows a defined list of settings to change. """

    settings_list = list()
    is_custom_form = False

    def __init__(self, *args, **kwargs):
        if 'settings' in kwargs:
            self.settings_list = kwargs.pop('settings')
        if 'is_custom_form' in kwargs:
            self.is_custom_form = kwargs.pop('is_custom_form')

        super(SettingsListForm, self).__init__(*args, **kwargs)

        initial_values = {}
        for setting in self.settings_list:
            setting_obj = NdrCoreValue.get_or_initialize(setting)
            label = setting_obj.value_label
            if self.is_custom_form:
                label = f"{setting_obj.value_name}: {setting_obj.value_label}"

            if setting_obj.value_type == NdrCoreValue.ValueType.STRING:
                self.fields[f"save_{setting}"] = forms.CharField(label=label,
                                                                 required=False,
                                                                 max_length=100,
                                                                 help_text=setting_obj.value_help_text)
            elif setting_obj.value_type == NdrCoreValue.ValueType.INTEGER:
                self.fields[f"save_{setting}"] = forms.IntegerField(label=label,
                                                                    required=False,
                                                                    help_text=setting_obj.value_help_text)
            elif setting_obj.value_type == NdrCoreValue.ValueType.BOOLEAN:
                self.fields[f"save_{setting}"] = forms.BooleanField(label=label,
                                                                    required=False,
                                                                    help_text=setting_obj.value_help_text)
            elif setting_obj.value_type == NdrCoreValue.ValueType.LIST:
                self.fields[f"save_{setting}"] = forms.ChoiceField(label=label,
                                                                   required=False,
                                                                   choices=setting_obj.get_options(),
                                                                   help_text=setting_obj.value_help_text)
            elif setting_obj.value_type == NdrCoreValue.ValueType.URL:
                self.fields[f"save_{setting}"] = forms.URLField(label=label,
                                                                required=False,
                                                                help_text=setting_obj.value_help_text)

            initial_values[f"save_{setting}"] = setting_obj.get_value()

        self.initial = initial_values

    def save_list(self):
        for setting in self.settings_list:
            if f"save_{setting}" in self.data:
                obj = NdrCoreValue.objects.get(value_name=setting)
                obj.value_value = self.data[f"save_{setting}"]
                obj.save()
            else:
                # If the setting is not in the data and its type is BOOLEAN, it means it was unchecked.
                try:
                    obj = NdrCoreValue.objects.get(value_name=setting)
                    if obj.value_type == NdrCoreValue.ValueType.BOOLEAN:
                        obj.value_value = False
                        obj.save()
                except NdrCoreValue.DoesNotExist:
                    pass

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for setting in self.settings_list:
            cols = '12'
            if self.is_custom_form:
                cols = '11'

            form_row = Row(css_class='form-row')
            form_row.append(Column(f"save_{setting}", css_class=f'form-group col-md-{cols} mb-0'))

            if self.is_custom_form:
                col = Column(Div(
                    HTML('<p>'
                         '  <a href="{% url \'ndr_core:edit_setting\' \''+setting+'\' %}" class="btn btn-sm btn-secondary">'
                         '    <i class="fa-regular fa-pen-to-square"></i>'
                         '  </a> '
                         '<a href="{% url \'ndr_core:delete_setting\' \''+setting+'\'%}" class="btn btn-sm btn-danger">'
                         '    <i class="fa-regular fa-delete-left"></i>'
                         '  </a>'
                         '</p>'),
                    css_class="form-group"
                ), css_class='form-group col-md-1 mb-0')
                form_row.append(col)
            layout.append(form_row)

        layout.append(get_form_buttons('Save Settings'))
        return helper


class SettingForm(forms.ModelForm):
    """Base form to create or edit a custom Setting. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreValue
        fields = ['value_name', 'value_label', 'value_help_text', 'value_value']

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        layout = helper.layout = Layout()
        helper.form_method = "POST"

        form_row = Row(
            Column('value_name', css_class='form-group col-md-6 mb-0'),
            Column('value_label', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('value_help_text', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('value_value', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)
        return helper


class SettingCreateForm(SettingForm):
    """Form to create a custom setting. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(SettingCreateForm, self).helper
        helper.layout.append(get_form_buttons('Create New User Setting'))
        return helper


class SettingEditForm(SettingForm):
    """Form to edit a custom setting. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(SettingEditForm, self).helper
        helper.layout.append(get_form_buttons('Save User Setting'))
        return helper


class SettingsImportForm(forms.Form):
    """Form to import settings from a json file. """

    settings_file = forms.FileField(help_text='Select your exported settings file. '
                                              'Existing settings with identical names are updated.')

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = "POST"
        helper.layout = Layout()

        form_row = Row(
            Column('settings_file', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        helper.layout.append(form_row)

        helper.layout.append(get_form_buttons('Import Settings'))
        return helper
