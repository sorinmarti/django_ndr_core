"""Contains forms used in the NDRCore admin interface for the creation or edit of image objects."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreImage


class ImageForm(forms.ModelForm):
    """Form to upload image data. """

    class Meta:
        model = NdrCoreImage
        fields = ['image_group', 'image', 'title', 'caption', 'citation', 'url']

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('image_group', css_class='form-group col-md-6 mb-0'),
            Column('image', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('title', css_class='form-group col-md-6 mb-0'),
            Column('caption', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('citation', css_class='form-group col-md-6 mb-0'),
            Column('url', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)
        return helper


class ImageCreateForm(ImageForm):

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(ImageCreateForm, self).helper
        helper.layout.append(get_form_buttons('Upload Image'))
        return helper


class ImageEditForm(ImageForm):

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(ImageEditForm, self).helper
        helper.layout.append(get_form_buttons('Save Image'))
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
