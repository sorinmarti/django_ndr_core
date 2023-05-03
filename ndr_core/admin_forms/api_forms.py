"""Contains forms used in the NDRCore admin interface for the creation or edit of API configurations."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreApiConfiguration


class ApiForm(forms.ModelForm):
    """Base form to create or edit an API configuration. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreApiConfiguration
        fields = ['api_name', 'api_host', 'api_protocol', 'api_port', 'api_label',
                  'api_page_size', 'api_url_stub', 'api_description', 'api_type',
                  'api_user_name', 'api_password', 'api_auth_key']
        widgets = {
            'api_description': forms.TextInput(attrs={}),
        }

    def __init__(self, *args, **kwargs):
        """This form will create the ApiConfiguration object but also translation objects to render the results.
        All the fields to create these objects are initialized here. """
        super(ApiForm, self).__init__(*args, **kwargs)

        target_fields = ["page_image", "fragment_image"]
        target_fields += ["" for x in range(10-len(target_fields))]

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('api_type', css_class='form-group col-md-3 mb-0'),
            Column('api_name', css_class='form-group col-md-3 mb-0'),
            Column('api_label', css_class='form-group col-md-4 mb-0'),
            Column('api_page_size', css_class='form-group col-md-2 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('api_protocol', css_class='form-group col-md-2 mb-0'),
            Column('api_host', css_class='form-group col-md-4 mb-0'),
            Column('api_port', css_class='form-group col-md-2 mb-0'),
            Column('api_url_stub', css_class='form-group col-md-4 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('api_user_name', css_class='form-group col-md-3 mb-0'),
            Column('api_password', css_class='form-group col-md-3 mb-0'),
            Column('api_auth_key', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('api_description', css_class='form-group col-md-12 mb-0'),
            css_class='form-row')
        layout.append(form_row)

        # helper.form_show_labels = False

        return helper


class ApiCreateForm(ApiForm):
    """Form to create an API configuration. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(ApiCreateForm, self).helper
        helper.layout.append(get_form_buttons('Create API Configuration'))
        return helper


class ApiEditForm(ApiForm):
    """Form to edit an API configuration. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(ApiEditForm, self).helper
        helper.layout.append(get_form_buttons('Save API Configuration'))
        return helper
