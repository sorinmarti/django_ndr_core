"""Contains forms used in the NDRCore admin interface for the creation or edit of sample data."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.models import NdrCoreApiConfiguration
from ndr_core.admin_forms.admin_forms import get_form_buttons


class SampleDataUploadForm(forms.Form):
    """Form to upload sample data. """

    api_to_upload_to = forms.ModelChoiceField(queryset=NdrCoreApiConfiguration.objects.all().order_by('api_label'),
                                              help_text='Sample Data depends on your configured API')
    upload_file = forms.FileField(help_text='Select a JSON file to upload')
    overwrite_files = forms.BooleanField(required=False, help_text='Overwrite Files with the same name?')

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('api_to_upload_to', css_class='form-group col-md-6 mb-0'),
            Column('upload_file', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('overwrite_files', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        helper.layout.append(get_form_buttons('Upload File'))
        return helper


class SampleDataDeleteForm(forms.Form):
    """ Form to confirm deletion of sample data file."""

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = "POST"
        helper.layout = Layout()
        helper.layout.append(get_form_buttons('Confirm Delete'))
        return helper
