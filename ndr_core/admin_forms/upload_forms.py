"""Contains forms used in the NDRCore admin interface for the creation or edit of image objects."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUpload


class UploadForm(forms.ModelForm):
    """Form to upload downloadable files. """

    class Meta:
        model = NdrCoreUpload
        fields = ['title', 'file']

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('title', css_class='form-group col-md-6 mb-0'),
            Column('file', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        return helper


class UploadCreateForm(UploadForm):
    """Form to upload downloadable files."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UploadCreateForm, self).helper
        helper.layout.append(get_form_buttons('Upload File'))
        return helper


class UploadEditForm(UploadForm):
    """Form to edit downloadable files."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UploadEditForm, self).helper
        helper.layout.append(get_form_buttons('Save File'))
        return helper
