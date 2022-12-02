from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreValue


class SettingsForm(forms.Form):
    """TODO """

    settings_list = list()

    def __init__(self, *args, **kwargs):
        if 'settings' in kwargs:
            self.settings_list = kwargs.pop('settings')

        super(SettingsForm, self).__init__(*args, **kwargs)

        for setting in self.settings_list:
            try:
                setting_obj = NdrCoreValue.objects.get(value_name=setting)
                self.fields[setting] = forms.CharField(label=setting_obj.value_label,
                                                       required=False,
                                                       max_length=100,
                                                       help_text=setting_obj.value_help_text)
            except NdrCoreValue.DoesNotExist:
                pass

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()
        layout.append(get_form_buttons('Save Settings'))
        return helper


class SettingForm(forms.ModelForm):
    """Base form to create or edit a custom Setting. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreValue
        fields = ['value_name', 'value_label', 'value_help_text', 'value_value']

    def __init__(self, *args, **kwargs):
        """Init class and create form helper."""
        super(SettingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"


class SettingCreateForm(SettingForm):
    """Form to create a custom setting. Extends the base form class and adds a 'create' button."""

    def __init__(self, *args, **kwargs):
        """Init the form and add the 'create' button."""
        super(SettingCreateForm, self).__init__(*args, **kwargs)
        self.helper.add_input(Submit('submit', 'Create New Setting'))