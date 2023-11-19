"""Contains forms used in the NDRCore admin interface for the creation or edit of result fields."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons, get_info_box
from ndr_core.models import NdrCoreResultField


class ResultFieldForm(forms.ModelForm):
    """Form to create or edit a search field form. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreResultField
        fields = ['expression', 'rich_expression', 'field_type', 'field_filter', 'display_border',
                  'html_display', 'md_display', 'field_classes']

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        layout = helper.layout = Layout()
        helper.form_method = "POST"

        form_row = Row(
            Column('field_type', css_class='form-group col-6'),
            Column(
                get_info_box('', 'page_type_info'),
                css_class='form-group col-6'
            ),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('field_filter', css_class='form-group col-6'),
            Column(
                get_info_box('Here comes information about the filters',
                             item_id='none',
                             box_id='filter_info_box'),
                css_class='form-group col-6'
            ),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('expression', css_class='form-group col-12'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('rich_expression', css_class='form-group col-12'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('field_classes', css_class='form-group col-12'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('display_border', css_class='form-group col-4'),
            Column('html_display', css_class='form-group col-4'),
            Column('md_display', css_class='form-group col-4'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column(
                get_info_box('Access your variables in the following form', 'xxx_info'),
                css_class='form-group col-12'
            ),
            css_class='form-row'
        )
        layout.append(form_row)

        return helper


class ResultFieldCreateForm(ResultFieldForm):
    """Form to create a search field form. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Search Field'))
        return helper


class ResultFieldEditForm(ResultFieldForm):
    """Form to edit a search field form. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save Search Field'))
        return helper
