"""Contains forms used in the NDRCore admin interface for the creation or edit of image objects."""
import json
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms
from django.core.exceptions import ValidationError

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUpload, NdrCoreManifest, NdrCoreManifestGroup
import zipfile


# Maximum file size in bytes (default: 100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

# Allowed MIME types for general uploads (None = allow all)
ALLOWED_MIME_TYPES = None  # Or specify like ['application/pdf', 'audio/mpeg', etc.]


class UploadForm(forms.ModelForm):
    """Form to upload downloadable files. """

    class Meta:
        model = NdrCoreUpload
        fields = ['title', 'file']

    def clean_file(self):
        """Validate uploaded file."""
        file = self.cleaned_data.get('file')

        if file:
            # Check file size
            if file.size > MAX_FILE_SIZE:
                size_mb = MAX_FILE_SIZE / (1024 * 1024)
                raise ValidationError(
                    f'File size exceeds maximum allowed size of {size_mb:.0f}MB. '
                    f'Your file is {file.size / (1024 * 1024):.1f}MB.'
                )

            # Check MIME type if restrictions are configured
            if ALLOWED_MIME_TYPES and file.content_type not in ALLOWED_MIME_TYPES:
                raise ValidationError(
                    f'File type "{file.content_type}" is not allowed. '
                    f'Allowed types: {", ".join(ALLOWED_MIME_TYPES)}'
                )

        return file

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('title', css_class='form-group col-md-6 mb-0'),
            Column('file', css_class='form-group col-md-6 mb-0'),
            css_class='row g-2'
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
        fields = ['identifier', 'title', 'file', 'manifest_group']

    def clean_file(self):
        """Validate uploaded manifest file."""
        file = self.cleaned_data.get('file')

        if file:
            # Check file size
            if file.size > MAX_FILE_SIZE:
                size_mb = MAX_FILE_SIZE / (1024 * 1024)
                raise ValidationError(
                    f'File size exceeds maximum allowed size of {size_mb:.0f}MB. '
                    f'Your file is {file.size / (1024 * 1024):.1f}MB.'
                )

            # Validate that it's a JSON file
            if not file.name.lower().endswith('.json'):
                raise ValidationError('Manifest files must be in JSON format (.json extension required).')

            # Try to parse JSON and validate basic IIIF structure
            try:
                file.seek(0)  # Reset file pointer
                manifest_data = json.load(file)
                file.seek(0)  # Reset again for Django to process

                # Basic IIIF manifest validation
                if '@context' not in manifest_data:
                    raise ValidationError('Invalid IIIF manifest: missing @context field.')

                if 'sequences' not in manifest_data and 'items' not in manifest_data:
                    raise ValidationError(
                        'Invalid IIIF manifest: missing sequences (v2) or items (v3) field.'
                    )

            except json.JSONDecodeError as e:
                raise ValidationError(f'Invalid JSON file: {str(e)}')
            except Exception as e:
                raise ValidationError(f'Error validating manifest: {str(e)}')

        return file

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('manifest_group', css_class='form-group col-md-6 mb-0'),
            Column('identifier', css_class='form-group col-md-6 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('title', css_class='form-group col-md-6 mb-0'),
            Column('file', css_class='form-group col-md-6 mb-0'),
            css_class='row g-2'
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
            css_class='row g-2'
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


class ManifestBulkUploadForm(forms.Form):
    """Form to upload a ZIP file containing multiple manifest files."""

    manifest_group = forms.ModelChoiceField(
        queryset=NdrCoreManifestGroup.objects.all(),
        required=False,
        help_text='Select an existing group or leave blank to create a new one'
    )
    new_group_title = forms.CharField(
        max_length=255,
        required=False,
        help_text='Title for new manifest group (only if no group selected above)'
    )
    zip_file = forms.FileField(
        help_text='ZIP file containing IIIF manifest JSON files (max 100MB)'
    )

    def clean_zip_file(self):
        """Validate uploaded ZIP file."""
        file = self.cleaned_data.get('zip_file')

        if file:
            # Check file size
            if file.size > MAX_FILE_SIZE:
                size_mb = MAX_FILE_SIZE / (1024 * 1024)
                raise ValidationError(
                    f'File size exceeds maximum allowed size of {size_mb:.0f}MB. '
                    f'Your file is {file.size / (1024 * 1024):.1f}MB.'
                )

            # Validate that it's a ZIP file
            if not file.name.lower().endswith('.zip'):
                raise ValidationError('File must be a ZIP archive (.zip extension required).')

            # Try to open as ZIP
            import zipfile
            try:
                file.seek(0)
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    # Check for any JSON files
                    json_files = [f for f in zip_ref.namelist()
                                  if f.lower().endswith('.json') and not f.startswith('__MACOSX')]
                    if not json_files:
                        raise ValidationError('ZIP file does not contain any JSON files.')
                file.seek(0)  # Reset for Django to process
            except zipfile.BadZipFile:
                raise ValidationError('Invalid ZIP file.')
            except Exception as e:
                raise ValidationError(f'Error reading ZIP file: {str(e)}')

        return file

    def clean(self):
        """Validate that either a group is selected or a new group title is provided."""
        cleaned_data = super().clean()
        manifest_group = cleaned_data.get('manifest_group')
        new_group_title = cleaned_data.get('new_group_title')

        if not manifest_group and not new_group_title:
            raise ValidationError(
                'Please either select an existing manifest group or provide a title for a new group.'
            )

        return cleaned_data

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('manifest_group', css_class='form-group col-md-6 mb-0'),
            Column('new_group_title', css_class='form-group col-md-6 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('zip_file', css_class='form-group col-md-12 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        layout.append(get_form_buttons('Upload ZIP'))

        return helper
