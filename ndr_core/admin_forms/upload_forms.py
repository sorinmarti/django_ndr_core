"""Contains forms used in the NDRCore admin interface for the creation or edit of image objects."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUpload, NdrCoreManifest, NdrCoreManifestGroup


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
        helper = super().helper
        helper.layout.append(get_form_buttons('Upload File'))
        return helper


class UploadEditForm(UploadForm):
    """Form to edit downloadable files."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save File'))
        return helper


class ManifestUploadForm(forms.ModelForm):
    """Form to upload manifest files. """

    class Meta:
        model = NdrCoreManifest
        fields = ['title', 'file', 'manifest_group']

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('manifest_group', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('title', css_class='form-group col-md-6 mb-0'),
            Column('file', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        return helper


class ManifestUploadCreateForm(ManifestUploadForm):
    """Form to upload downloadable files."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Upload Manifest File'))
        return helper


class ManifestUploadEditForm(ManifestUploadForm):
    """Form to edit downloadable files."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save Manifest File'))
        return helper


class ManifestGroupForm(forms.ModelForm):
    """Form to upload manifest files. """

    class Meta:
        model = NdrCoreManifestGroup
        fields = ['title', 'order_value_1_title', 'order_value_2_title', 'order_value_3_title']

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('title', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column("order_value_1_title", css_class="form-group col-md-4 mb-0"),
            Column("order_value_2_title", css_class="form-group col-md-4 mb-0"),
            Column("order_value_3_title", css_class="form-group col-md-4 mb-0"),
            css_class="form-row"
        )
        layout.append(form_row)

        return helper


class ManifestGroupCreateForm(ManifestGroupForm):
    """Form to upload downloadable files."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Manifest Group'))
        return helper


class ManifestGroupEditForm(ManifestGroupForm):
    """Form to edit downloadable files."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save Manifest Group'))
        return helper
