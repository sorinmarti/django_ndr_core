"""Contains forms used in the NDRCore admin interface for the creation or edit of Search form configurations."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, HTML
from django import forms

from ndr_core.forms.widgets import CSVTextEditorWidget
from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreSearchField


class SearchFieldForm(forms.ModelForm):
    """Form to create or edit a search field form. """

    def __init__(self, *args, **kwargs):
        """Initializes the form with the provided arguments."""
        super().__init__(*args, **kwargs)

        self.fields['list_choices'] = forms.CharField(widget=CSVTextEditorWidget(
            attrs={'instance': kwargs.get('instance', None), 'type_field_id': 'id_field_type'}),
            help_text="key, value, value_{lang}, is_searchable, is_printable, info, info_{lang}")

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreSearchField
        fields = ['field_name', 'field_label', 'field_type', 'field_required', 'help_text', 'api_parameter',
                  'lower_value', 'upper_value', 'list_choices', 'use_in_csv_export', 'initial_value', 'data_field_type',
                  'input_transformation_regex', 'list_condition', 'comparison_operator', 'text_choices']

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        layout = helper.layout = Layout()
        helper.form_id = "search_field_form"
        helper.form_method = "POST"

        # ----------------------------------------------------------------------------------------------------------

        form_row = Row(
            Column(Div(HTML('''
                            <br/>
                            <b>1.) Select the type of Search Field you want to create.</b>
                            &nbsp;&nbsp; 
                            <small></small>
                            <hr/>
                            ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        html = HTML('<div id="div_id_info_text" class="alert alert-primary small" role="alert">'
                    '  <b id="id_info_text_title" style="margin-right: 1rem;">'
                    '  Field Type</b>(<span id="id_info_text_text">Info</span>)<br/>'
                    '  <p style="margin-top: 1rem;"><i>Features:</i>'
                    '  <div id="id_info_text_detail">'
                    '    <ul>'
                    '      <li>do stuff</li>'
                    '    </ul>'
                    '  </div>'
                    '</div>')
        form_row = Row(
            Column('field_type', css_class='form-group col-5'),
            Column(html, css_class='form-group col-7'),
            css_class='row g-2'
        )
        layout.append(form_row)

        # ----------------------------------------------------------------------------------------------------------

        form_row = Row(
            Column(Div(HTML('''
                                    <br/>
                                    <b>2.) Choose a name and connect to API.</b>
                                    &nbsp;&nbsp; 
                                    <small></small>
                                    <hr/>
                                    ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('field_name', css_class='form-group col-6'),
            Column('api_parameter', css_class='form-group col-6'),
            css_class='row g-2'
        )
        layout.append(form_row)

        # ----------------------------------------------------------------------------------------------------------

        form_row = Row(
            Column(Div(HTML('''
                                    <br/>
                                    <b>3.) Enter the text your users can see.</b>
                                    &nbsp;&nbsp; 
                                    <small></small>
                                    <hr/>
                                    ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('field_label', css_class='form-group col-6'),
            Column('initial_value', css_class='form-group col-6'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('field_required', css_class='form-group col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('help_text', css_class='form-group col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        # ----------------------------------------------------------------------------------------------------------

        form_row = Row(
            Column(Div(HTML('''
                                    <br/>
                                    <b>4.) Specify field-related information.</b>
                                    &nbsp;&nbsp; 
                                    <small></small>
                                    <hr/>
                                    ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('list_condition', css_class='form-group col-4'),
            Column('lower_value', css_class='form-group col-4'),
            Column('upper_value', css_class='form-group col-4'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('comparison_operator', css_class='form-group col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('list_choices', css_class='form-group col-md-12 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('text_choices', css_class='form-group col-md-12 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        # ----------------------------------------------------------------------------------------------------------

        form_row = Row(
            Column(Div(HTML('''
                                    <br/>
                                    <b>5.) Additional Settings.</b>
                                    &nbsp;&nbsp; 
                                    <small></small>
                                    <hr/>
                                    ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column("data_field_type", css_class="form-group col-6"),
            Column('use_in_csv_export', css_class='form-group col-6'),
            css_class="form-row",
        )
        layout.append(form_row)

        form_row = Row(
            Column("input_transformation_regex", css_class="form-group col-12"),
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
        helper.layout.append(get_form_buttons('Create Search Field', include_save_and_continue=True))
        return helper


class SearchFieldEditForm(SearchFieldForm):
    """Form to edit a search field form. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save Search Field', include_save_and_continue=True))
        return helper
