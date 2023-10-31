"""Contains forms used in the NDRCore admin interface for the creation or edit of Search form configurations."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Field, HTML, Submit, Button
from django import forms
from django.core.exceptions import ValidationError

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreSearchConfiguration, NdrCoreSearchField


class SearchConfigurationForm(forms.ModelForm):
    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreSearchConfiguration
        fields = ['conf_name', 'conf_label',
                  'api_type', 'api_connection_url',
                  'api_user_name', 'api_password', 'api_auth_key',
                  'search_id_field', 'sort_field', 'simple_query_main_field',
                  'search_has_compact_result', 'page_size', 'repository_url']

    def __init__(self, *args, **kwargs):
        super(SearchConfigurationForm, self).__init__(*args, **kwargs)

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
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('conf_name', css_class='col-6'),
            Column('conf_label', css_class='col-6'),
            css_class='form-row'
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
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('api_type', css_class='col-4'),
            Column('api_connection_url', css_class='col-8'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('api_user_name', css_class='col-3'),
            Column('api_password', css_class='col-3'),
            Column('api_auth_key', css_class='col-6'),
            css_class='form-row'
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
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('search_id_field', css_class='col-4'),
            Column('sort_field', css_class='col-4'),
            Column('simple_query_main_field', css_class='col-4'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('search_has_compact_result', css_class='col-3'),
            Column('page_size', css_class='col-3'),
            Column('repository_url', css_class='col-6'),
            css_class='form-row'
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
        helper = super(SearchConfigurationCreateForm, self).helper
        helper.layout.append(get_form_buttons('Create Search Configuration'))
        return helper


class SearchConfigurationEditForm(SearchConfigurationForm):
    """Form to create a search field form. """

    @property
    def helper(self):
        helper = super(SearchConfigurationEditForm, self).helper
        helper.layout.append(get_form_buttons('Edit Search Configuration'))
        return helper


class SearchConfigurationFormEditForm(forms.ModelForm):
    """Form to create or edit a search configuration. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreSearchConfiguration
        fields = ['conf_name', ]

    def __init__(self, *args, **kwargs):
        super(SearchConfigurationFormEditForm, self).__init__(*args, **kwargs)

        for search_field_conf_row in range(20):
            required = False
            if search_field_conf_row == 0:
                required = True

            search_field = forms.ModelChoiceField(queryset=NdrCoreSearchField.objects.all(),
                                                  required=required, help_text="")
            row_field = forms.IntegerField(required=required,
                                           help_text="")
            column_field = forms.IntegerField(required=required,
                                              help_text="")
            size_field = forms.IntegerField(required=required, help_text="")

            self.fields[f'search_field_{search_field_conf_row}'] = search_field
            self.fields[f'row_field_{search_field_conf_row}'] = row_field
            self.fields[f'column_field_{search_field_conf_row}'] = column_field
            self.fields[f'size_field_{search_field_conf_row}'] = size_field

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Div(css_class='form-row', css_id=f'search_field_config_title_row')
        form_row.append(Div(HTML('Search Field'), css_class='col-md-6'))
        form_row.append(Div(HTML('Row (1-?)'), css_class='col-md-2'))
        form_row.append(Div(HTML('Column (1-12)'), css_class='col-md-2'))
        form_row.append(Div(HTML('Size (1-12)'), css_class='col-md-2'))
        layout.append(form_row)

        for row in range(20):
            form_row = Div(css_class='form-row', css_id=f'search_field_config_row_{row}')
            form_field_search_field = Field(f'search_field_{row}', placeholder=f"Search Field {row+1}", wrapper_class=f'col-md-6')
            form_field_row_field = Field(f'row_field_{row}', placeholder=f"Row", wrapper_class=f'col-md-2')
            form_field_column_field = Field(f'column_field_{row}', placeholder="Column", wrapper_class=f'col-md-2')
            form_field_size_field = Field(f'size_field_{row}', placeholder="Size", wrapper_class=f'col-md-2')

            form_row.append(form_field_search_field)
            form_row.append(form_field_row_field)
            form_row.append(form_field_column_field)
            form_row.append(form_field_size_field)

            layout.append(form_row)

        helper.form_show_labels = False

        form_row = Row(
            Column(HTML('<img id="preview_search_form_image" />'), css_class='col-md-12'),
            css_class='form-row'
        )
        layout.append(form_row)

        helper.add_input(Submit('submit', 'Create Search Configuration'))
        helper.add_input(Button('add_row', 'Add Row', css_class='btn btn-secondary'))
        helper.add_input(Button('remove_row', 'Remove Row', css_class='btn btn-secondary'))

        return helper
