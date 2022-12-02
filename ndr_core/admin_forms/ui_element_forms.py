from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUIElement


class UIElementForm(forms.ModelForm):
    """Base form to create or edit an UI Element."""

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreUIElement
        fields = ['element_type', ]

    def __init__(self, *args, **kwargs):
        """Init class and create form helper."""
        super(UIElementForm, self).__init__(*args, **kwargs)

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('element_type', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        return helper


class UIElementCreateForm(UIElementForm):
    """Form to create a UI Element. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementCreateForm, self).helper
        helper.layout.append(get_form_buttons('Create New UI Element'))
        return helper


class UIElementEditForm(UIElementForm):
    """Form to edit a UI Element. Extends the base form class and adds an 'edit' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementEditForm, self).helper
        helper.layout.append(get_form_buttons('Save UI Element'))
        return helper
