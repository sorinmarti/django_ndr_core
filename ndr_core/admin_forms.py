from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Field, Layout, HTML, Button
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django_select2 import forms as s2forms

from ndr_core.models import NdrCorePage, ApiConfiguration, NdrSearchField, SearchConfiguration, \
    FilterableListConfiguration


class SearchConfigurationWidget(s2forms.ModelSelect2MultipleWidget):
    model = SearchConfiguration
    search_fields = [
        'conf_name__icontains'
    ]


class FilteredListWidget(s2forms.ModelSelect2MultipleWidget):
    model = FilterableListConfiguration
    search_fields = [
        'list_name__icontains'
    ]


class PageForm(forms.ModelForm):
    search_configs = forms.ModelMultipleChoiceField(queryset=SearchConfiguration.objects.filter().order_by('conf_name'),
                                            required=False,
                                            widget=SearchConfigurationWidget(attrs={'data-minimum-input-length': 0}))

    list_configs = forms.ModelMultipleChoiceField(queryset=FilterableListConfiguration.objects.all().order_by('list_name'),
                                          required=False,
                                          widget=SearchConfigurationWidget(attrs={'data-minimum-input-length': 0}))

    class Meta:
        model = NdrCorePage
        fields = ['name', 'label', 'page_type', 'search_configs', 'list_configs', 'view_name']

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('submit', 'Create New Page'))

    def clean_search_configs(self):
        page_type = self.cleaned_data['page_type']
        data = self.cleaned_data['search_configs']
        print(data, NdrCorePage.PageType.SEARCH, page_type)
        if data.count() == 0 and page_type == NdrCorePage.PageType.SEARCH:
            raise ValidationError("Choose a Search Configuration")
        return data


class ApiForm(forms.ModelForm):
    class Meta:
        model = ApiConfiguration
        fields = ['api_name', 'api_host', 'api_protocol', 'api_port', 'api_label', 'api_page_size']

    def __init__(self, *args, **kwargs):
        super(ApiForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('submit', 'Create Api Configuration'))


class SearchFieldForm(forms.ModelForm):
    class Meta:
        model = NdrSearchField
        fields = ['field_name', 'field_label', 'field_type', 'field_required', 'help_text', 'api_parameter']

    def __init__(self, *args, **kwargs):
        super(SearchFieldForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('submit', 'Create Search Field'))


class SearchConfigurationForm(forms.ModelForm):

    class Meta:
        model = SearchConfiguration
        fields = ['conf_name', 'api_configuration']

    def __init__(self, *args, **kwargs):
        super(SearchConfigurationForm, self).__init__(*args, **kwargs)

        for search_field_conf_row in range(20):
            required = False
            if search_field_conf_row == 0:
                required = True

            search_field = forms.ModelChoiceField(queryset=NdrSearchField.objects.all(),
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
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        layout.append(Div(Field('conf_name', wrapper_class=f'col-md-12'), css_class='form-row'))
        layout.append(Div(Field('api_configuration', wrapper_class=f'col-md-12'), css_class='form-row'))

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

        helper.add_input(Submit('submit', 'Create Search Configuration'))
        helper.add_input(Button('add_row', 'Add Row', css_class='btn btn-secondary'))
        helper.add_input(Button('remove_row', 'Remove Row', css_class='btn btn-secondary'))
        return helper


class NdrCoreLoginForm(AuthenticationForm):
    """Takes Django's login form and adds an input to it so it can be rendered with crispy forms """

    def __init__(self, *args, **kwargs):
        super(NdrCoreLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('login', 'Login'))