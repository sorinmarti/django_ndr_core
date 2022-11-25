"""Contains all forms used in the NDRCore admin interface."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Field, Layout, HTML, Button
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django_select2 import forms as s2forms

from ndr_core.models import NdrCorePage, NdrCoreApiConfiguration, NdrCoreSearchField, NdrCoreSearchConfiguration, \
    NdrCoreFilterableListConfiguration


class SearchConfigurationWidget(s2forms.ModelSelect2MultipleWidget):
    """Widget to display a multi select2 dropdown for search configurations. """

    model = NdrCoreSearchConfiguration
    search_fields = [
        'conf_name__icontains'
    ]


class FilteredListWidget(s2forms.ModelSelect2MultipleWidget):
    """Widget to display a multi select2 dropdown for list configurations. """

    model = NdrCoreFilterableListConfiguration
    search_fields = [
        'list_name__icontains'
    ]


class PageForm(forms.ModelForm):
    """Base form to create or edit an NDRCore page. The form contains fields for search configurations etc. which are only needed
    for certain page types. Unused fields are hidden via JS in the template the form is used."""

    search_configs = forms.ModelMultipleChoiceField(
        queryset=NdrCoreSearchConfiguration.objects.filter().order_by('conf_name'),
        required=False,
        widget=SearchConfigurationWidget(
            attrs={'data-minimum-input-length': 0}))

    list_configs = forms.ModelMultipleChoiceField(queryset=NdrCoreFilterableListConfiguration.objects.all().\
                                                  order_by('list_name'),
                                                  required=False,
                                                  widget=FilteredListWidget(
                                                      attrs={'data-minimum-input-length': 0}))

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCorePage
        fields = ['name', 'label', 'page_type',
                  'simple_api', 'search_configs', 'list_configs', 'view_name', 'template_text']

    def __init__(self, *args, **kwargs):
        """Init class and create form helper."""
        super(PageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"

    def clean(self):
        """clean() is executed when the form is sent to check it. Here, page types are checked against its
        requirements. Example: A simple search needs an API config but no List- and SearchConfiguration."""
        cleaned_data = super().clean()
        page_type = cleaned_data['page_type']
        search_configs = cleaned_data['search_configs']
        list_configs = cleaned_data['list_configs']
        simple_api = cleaned_data['simple_api']

        if page_type == NdrCorePage.PageType.TEMPLATE:
            # no additional fields required
            pass
        elif page_type == NdrCorePage.PageType.SIMPLE_SEARCH:
            if simple_api is None:
                msg = "You must provide an API configuration for Simple Search pages."
                self.add_error('simple_api', msg)
        elif page_type == NdrCorePage.PageType.SEARCH:
            if search_configs.count() == 0:
                msg = "You must provide at least one Search configuration for Search pages."
                self.add_error('search_configs', msg)
        elif page_type == NdrCorePage.PageType.COMBINED_SEARCH:
            if search_configs.count() == 0:
                msg = "You must provide at least one Search configuration for Combined Search pages."
                self.add_error('search_configs', msg)
            if simple_api is None:
                msg = "You must provide an API configuration for Combined Search pages."
                self.add_error('simple_api', msg)
        elif page_type == NdrCorePage.PageType.FILTER_LIST:
            if list_configs.count() == 0:
                msg = "You must provide at least one List configuration for List pages."
                self.add_error('list_configs', msg)
        elif page_type == NdrCorePage.PageType.CONTACT:
            if NdrCorePage.objects.filter(page_type=NdrCorePage.PageType.CONTACT).count() > 0:
                msg = "You can't have more than one contact page."
                self.add_error('page_type', msg)
        else:
            pass


class PageCreateForm(PageForm):
    """Form to create a page. Extends the base form class and adds a 'create' button."""

    def __init__(self, *args, **kwargs):
        """Init the form and add the 'create' button."""
        super(PageCreateForm, self).__init__(*args, **kwargs)
        self.helper.add_input(Submit('submit', 'Create New Page'))
        
        
class PageEditForm(PageForm):
    """Form to edit a page. Extends the base form class and adds an 'edit' button."""

    def __init__(self, *args, **kwargs):
        """Init the form and add the 'edit' button."""
        super(PageEditForm, self).__init__(*args, **kwargs)
        self.helper.add_input(Submit('submit', 'Save Page'))
    
    
class ApiForm(forms.ModelForm):
    """Base form to create or edit an API configuration. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreApiConfiguration
        fields = ['api_name', 'api_host', 'api_protocol', 'api_port', 'api_label', 'api_page_size', 'api_url_stub']

    def __init__(self, *args, **kwargs):
        """This form will create the ApiConfiguration object but also translation objects to render the results.
        All the fields to create these objects are initialized here. """
        super(ApiForm, self).__init__(*args, **kwargs)

        target_fields = ["page_image", "fragment_image"]
        target_fields += ["" for x in range(10-len(target_fields))]

        for rendering_conf_row in range(10):
            required = False
            if rendering_conf_row == 0:
                required = True

            target_field_name = forms.CharField(required=required, help_text="")
            field_label = forms.CharField(required=required, help_text="")
            source_field_name = forms.CharField(required=required, help_text="")
            alternate_field_name = forms.CharField(required=required, help_text="")
            field_none_value = forms.CharField(required=required, help_text="")

            self.fields[f'target_field_name_{rendering_conf_row}'] = target_field_name
            self.fields[f'field_label_{rendering_conf_row}'] = field_label
            self.fields[f'source_field_name_{rendering_conf_row}'] = source_field_name
            self.fields[f'alternate_field_name_{rendering_conf_row}'] = alternate_field_name
            self.fields[f'field_none_value_{rendering_conf_row}'] = field_none_value

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        layout.append(
            Div(Field('api_name', wrapper_class=f'col-md-5'),
                Field('api_label', wrapper_class=f'col-md-5'),
                Field('api_page_size', wrapper_class=f'col-md-2'),
                css_class='form-row')
        )

        layout.append(
            Div(Field('api_protocol', wrapper_class=f'col-md-2'),
                Field('api_host', wrapper_class=f'col-md-4'),
                Field('api_port', wrapper_class=f'col-md-2'),
                Field('api_url_stub', wrapper_class=f'col-md-4'),
                css_class='form-row')
        )

        form_row = Div(css_class='form-row', css_id=f'rendering_config_title_row')
        form_row.append(Div(HTML('Template'), css_class='col-md-2'))
        form_row.append(Div(HTML('Label'), css_class='col-md-2'))
        form_row.append(Div(HTML('API Result Field'), css_class='col-md-3'))
        form_row.append(Div(HTML('Alt. API Result Field'), css_class='col-md-3'))
        form_row.append(Div(HTML('None Value'), css_class='col-md-2'))
        layout.append(form_row)

        for row in range(10):
            form_row = Div(css_class='form-row', css_id=f'rendering_config_row_{row}')
            form_field_target_field_name = Field(f'target_field_name_{row}', wrapper_class=f'col-md-2')
            form_field_field_label = Field(f'field_label_{row}', wrapper_class=f'col-md-2')
            form_field_source_field_name = Field(f'source_field_name_{row}', wrapper_class=f'col-md-3')
            form_field_alternate_field_name = Field(f'alternate_field_name_{row}', wrapper_class=f'col-md-3')
            form_field_field_none_value = Field(f'field_none_value_{row}', wrapper_class=f'col-md-2')

            form_row.append(form_field_target_field_name)
            form_row.append(form_field_field_label)
            form_row.append(form_field_source_field_name)
            form_row.append(form_field_alternate_field_name)
            form_row.append(form_field_field_none_value)

            layout.append(form_row)

        helper.form_show_labels = False

        return helper


class ApiCreateForm(ApiForm):
    """Form to create an API configuration. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(ApiCreateForm, self).helper

        helper.add_input(Submit('submit', 'Create API Configuration'))
        helper.add_input(Button('add_row', 'Add Row', css_class='btn btn-secondary'))
        helper.add_input(Button('remove_row', 'Remove Row', css_class='btn btn-secondary'))

        return helper


class ApiEditForm(ApiForm):
    """Form to edit an API configuration. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(ApiEditForm, self).helper

        helper.add_input(Submit('submit', 'Save API Configuration'))
        helper.add_input(Button('add_row', 'Add Row', css_class='btn btn-secondary'))
        helper.add_input(Button('remove_row', 'Remove Row', css_class='btn btn-secondary'))

        return helper


class SearchFieldForm(forms.ModelForm):
    """Form to create or edit a search field form. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreSearchField
        fields = ['field_name', 'field_label', 'field_type', 'field_required', 'help_text', 'api_parameter']

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = "POST"
        return helper


class SearchFieldCreateForm(SearchFieldForm):
    """Form to create a search field form. """

    @property
    def helper(self):
        helper = super(SearchFieldCreateForm, self).helper
        helper.add_input(Submit('submit', 'Create Search Field'))
        return helper


class SearchFieldEditForm(SearchFieldForm):
    """Form to edit a search field form. """

    @property
    def helper(self):
        helper = super(SearchFieldEditForm, self).helper
        helper.add_input(Submit('submit', 'Save Search Field'))
        return helper


class SearchConfigurationForm(forms.ModelForm):
    """Form to create or edit a search search configuration. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreSearchConfiguration
        fields = ['conf_name', 'api_configuration']

    def __init__(self, *args, **kwargs):
        super(SearchConfigurationForm, self).__init__(*args, **kwargs)

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

    def clean_conf_name(self):
        """Check if conf_name is not a reserved name. """
        data = self.cleaned_data['conf_name']
        if data == 'simple':
            raise ValidationError("'simple' is a reserved term and can't be used")
        return data

    @property
    def helper(self):
        """Creates and returns the form helper property."""
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


class SearchConfigurationCreateForm(SearchConfigurationForm):
    """Form to create a search search configuration. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(SearchConfigurationCreateForm, self).helper
        helper.add_input(Submit('submit', 'Create Search Configuration'))
        helper.add_input(Button('add_row', 'Add Row', css_class='btn btn-secondary'))
        helper.add_input(Button('remove_row', 'Remove Row', css_class='btn btn-secondary'))
        return helper


class SearchConfigurationEditForm(SearchConfigurationForm):
    """Form to edit a search search configuration. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(SearchConfigurationEditForm, self).helper
        helper.add_input(Submit('submit', 'Edit Search Configuration'))
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
