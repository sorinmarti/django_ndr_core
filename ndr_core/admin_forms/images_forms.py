from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreApiConfiguration


class ImageUploadForm(forms.Form):
    """Form to upload sample data. """

    group_to_upload_to = forms.ChoiceField(choices=[('1', 'one')],
                                           help_text='TODO')
    upload_file = forms.FileField(help_text='TODO')

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('group_to_upload_to', css_class='form-group col-md-6 mb-0'),
            Column('upload_file', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        helper.layout.append(get_form_buttons('Upload Image'))
        return helper


class LogoUploadForm(forms.Form):
    """Form to upload sample data. """

    upload_file = forms.FileField(help_text='TODO')

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('upload_file', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        helper.layout.append(get_form_buttons('Upload Logo'))
        return helper
