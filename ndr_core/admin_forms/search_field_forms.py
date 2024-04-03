"""Contains forms used in the NDRCore admin interface for the creation or edit of Search form configurations."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.forms.widgets import CSVTextEditorWidget
from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreSearchField


class SearchFieldForm(forms.ModelForm):
    """Form to create or edit a search field form. """

    def __init__(self, *args, **kwargs):
        """Initializes the form with the provided arguments."""
        super().__init__(*args, **kwargs)

        """self.fields['list_choices'] = forms.CharField(widget=CSVTextEditorWidget(
            attrs={'instance': kwargs.get('instance', None)}
        ))"""

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreSearchField
        fields = ['field_name', 'field_label', 'field_type', 'field_required', 'help_text', 'api_parameter',
                  'lower_value', 'upper_value', 'list_choices', 'use_in_csv_export', 'initial_value', 'data_field_type',
                  'input_transformation_regex']

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        layout = helper.layout = Layout()
        helper.form_method = "POST"

        form_row = Row(
            Column('field_label', css_class='form-group col-md-4 mb-0'),
            Column('field_name', css_class='form-group col-md-4 mb-0'),
            Column('api_parameter', css_class='form-group col-md-4 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('field_type', css_class='form-group col-md-6 mb-0'),
            Column('field_required', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('help_text', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('lower_value', css_class='form-group col-md-6 mb-0'),
            Column('upper_value', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('list_choices', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('use_in_csv_export', css_class='form-group col-md-6 mb-0'),
            Column('initial_value', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column("data_field_type", css_class="form-group col-md-6 mb-0"),
            Column("input_transformation_regex", css_class="form-group col-md-6 mb-0"),
            css_class="form-row",
        )
        layout.append(form_row)

        return helper


class SearchFieldCreateForm(SearchFieldForm):
    """Form to create a search field form. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Search Field'))
        return helper


class SearchFieldEditForm(SearchFieldForm):
    """Form to edit a search field form. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save Search Field'))
        return helper
