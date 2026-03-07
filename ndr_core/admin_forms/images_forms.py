"""Contains forms used in the NDRCore admin interface for the creation or edit of image objects."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons, get_info_box
from ndr_core.models import NdrCoreImage


class ImageForm(forms.ModelForm):
    """Simplified form to upload/edit images in the image library."""

    class Meta:
        model = NdrCoreImage
        fields = ['image', 'alt_text', 'image_active']

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        helper.form_enctype = 'multipart/form-data'
        layout = helper.layout = Layout()

        form_row = Row(
            Column(get_info_box("Upload an image to the library. "
                               "You can add contextual information (title, caption, etc.) "
                               "when using the image in UI Elements."),
                   css_class='form-group col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('image', css_class='form-group col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('alt_text', css_class='form-group col-9'),
            Column('image_active', css_class='form-group col-3'),
            css_class='row g-2'
        )
        layout.append(form_row)

        return helper


class ImageUploadForm(ImageForm):
    """Form to upload images to the library"""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Upload Image'))
        return helper


class ImageEditForm(ImageForm):
    """Form to edit images in the library"""

    class Meta:
        model = NdrCoreImage
        fields = ['image', 'alt_text', 'image_active']  # Allow changing the image file

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        # Update the info box for edit mode
        helper.layout[0] = Row(
            Column(get_info_box("Edit image information. "
                               "You can replace the image file if needed (e.g., replacing a placeholder with the actual image)."),
                   css_class='form-group col-12'),
            css_class='row g-2'
        )
        helper.layout.append(get_form_buttons('Save Changes'))
        return helper


class LogoUploadForm(forms.Form):
    """Form to upload the logo file """

    upload_file = forms.FileField(help_text='Choose a logo file to upload.')

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('upload_file', css_class='form-group col-md-12 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        helper.layout.append(get_form_buttons('Upload Logo'))
        return helper
