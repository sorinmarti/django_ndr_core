"""Contains forms used in the NDRCore admin interface for the creation or edit of Search form configurations."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, HTML
from django import forms
from django.core.exceptions import ValidationError

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreSearchConfiguration


class SearchConfigurationForm(forms.ModelForm):
    """Form to create or edit a search configuration search form. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreSearchConfiguration
        fields = ['conf_name', 'conf_label',
                  'api_type', 'api_connection_url',
                  'api_user_name', 'api_password', 'api_auth_key',
                  'search_id_field', 'sort_field', 'sort_order',
                  'search_has_compact_result', 'compact_result_is_default', 'page_size',
                  'compact_page_size', 'citation_expression', 'repository_url',
                  'has_simple_search', 'simple_search_first', 'simple_query_main_field',
                  'simple_query_label', 'simple_query_help_text', 'simple_search_tab_title',
                  'manifest_relation_expression', 'manifest_page_expression']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column(Div(HTML('''
            <br/>
            <b>1.) Provide a name and a label for your configuration</b>
            &nbsp;&nbsp; 
            <small>(Keep the name short and avoid special characters!))</small>
            <hr/>
            ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('conf_name', css_class='col-6'),
            Column('conf_label', css_class='col-6'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column(Div(HTML('''
                    <br/>
                    <b>2.) Configure the access to your data</b>
                    &nbsp;&nbsp; 
                    <small>(Select a type to see how to compose the connection string)</small>
                    <hr/>
                    ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('api_type', css_class='col-4'),
            Column('api_connection_url', css_class='col-8'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('api_user_name', css_class='col-3'),
            Column('api_password', css_class='col-3'),
            Column('api_auth_key', css_class='col-6'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column(Div(HTML('''
                            <br/>
                            <b>3.) Provide search configuration</b>
                            &nbsp;&nbsp; 
                            <small>()</small>
                            <hr/>
                            ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('search_id_field', css_class='col-4'),
            Column('sort_field', css_class='col-4'),
            Column('sort_order', css_class='col-4'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('search_has_compact_result', css_class='col-3'),
            Column('page_size', css_class='col-2'),
            Column('compact_page_size', css_class='col-2'),
            Column('repository_url', css_class='col-5'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('compact_result_is_default', css_class='col-3'),
            Column('citation_expression', css_class='col-9'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column(Div(HTML('''
                                    <br/>
                                    <b>4.) Simple Search</b>
                                    &nbsp;&nbsp; 
                                    <small>(Check the box if you want a single 
                                    field search with your search form.)</small>
                                    <hr/>
                                    ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('has_simple_search', css_class='col-4'),
            Column('simple_search_first', css_class='col-4'),
            Column('simple_query_main_field', css_class='col-4'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('simple_query_label', css_class='col-6'),
            Column('simple_search_tab_title', css_class='col-6'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('simple_query_help_text', css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('manifest_relation_expression', css_class='col-8'),
            Column('manifest_page_expression', css_class='col-4'),
            css_class='row g-2'
        )
        layout.append(form_row)

        return helper

    def clean_conf_name(self):
        """Check if conf_name is not a reserved name. """
        data = self.cleaned_data['conf_name']
        if data == 'simple':
            raise ValidationError("'simple' is a reserved term and can't be used")
        return data


class SearchConfigurationCreateForm(SearchConfigurationForm):
    """Form to create a search field form. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Search Configuration'))
        return helper


class SearchConfigurationEditForm(SearchConfigurationForm):
    """Form to create a search field form. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save Search Configuration'))
        return helper
