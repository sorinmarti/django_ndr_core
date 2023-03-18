import django.forms as forms
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML
from django_select2 import forms as s2forms


class RenderConfigurationForm(forms.Form):

    render_configuration = [{
        'field_name': 'test',
        'field_label': 'Title Line',
        'field_type': 'text'},
        {
        'field_name': 'test2',
        'field_label': 'First Text Line',
        'field_type': 'text'},
        {
        'field_name': 'test3',
        'field_label': 'Fragment Image',
        'field_type': 'text'}]

    def __init__(self, *args, **kwargs):
        """Initialises all needed form fields. """
        super().__init__(*args, **kwargs)

        for tab_conf in self.render_configuration:
            self.fields[f'{tab_conf["field_name"]}_renderer'] = forms.CharField(label="Renderer", required=False)
            self.fields[f'{tab_conf["field_name"]}_string_format'] = forms.CharField(label="String Format", required=False)
            for i in range(0, 4):
                self.fields[f'{tab_conf["field_name"]}_value_{i}'] = forms.CharField(label=f"Value {i+1}", required=False)
                self.fields[f'{tab_conf["field_name"]}_null_value_{i}'] = forms.CharField(label=f"Null Value {i+1}", required=False)

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Div(css_class='form-row')
        form_row.append(Div(HTML('<div class="alert alert-info">Bla</div>'), css_class='col-md-12'))
        layout.append(form_row)

        tabs = TabHolder(css_id='id_tabs')
        for tab_conf in self.render_configuration:

            tab = Tab(tab_conf["field_label"], css_id=tab_conf["field_name"])
            form_row = Div(css_class='form-row')
            form_field = Field(f'{tab_conf["field_name"]}_renderer',
                               wrapper_class=f'col-md-6')
            form_row.append(form_field)
            form_field = Field(f'{tab_conf["field_name"]}_string_format',
                               wrapper_class=f'col-md-6')
            form_row.append(form_field)
            tab.append(form_row)

            for i in range(0, 4):
                form_row = Div(css_class='form-row')
                form_field = Field(f'{tab_conf["field_name"]}_value_{i}',
                                   wrapper_class=f'col-md-6')
                form_row.append(form_field)

                form_field = Field(f'{tab_conf["field_name"]}_null_value_{i}',
                                   wrapper_class=f'col-md-6')
                form_row.append(form_field)

                tab.append(form_row)

            tabs.append(tab)

        layout.append(tabs)

        return helper


class RenderConfigurationForm(forms.Form):
    render_configuration = [
        {'field_name': 'test',
         'field_label': 'Title Line',
         'field_type': 'text'},
        {'field_name': 'test2',
         'field_label': 'First Text Line',
         'field_type': 'text'},
        {'field_name': 'test3',
         'field_label': 'Fragment Image',
         'field_type': 'text'}]

    def __init__(self, *args, **kwargs):
        """Initialises all needed form fields. """
        super().__init__(*args, **kwargs)

        for tab_conf in self.render_configuration:
            self.create_value_fields(tab_conf["field_name"])

    def create_value_fields(self, field_name):
        self.fields[f'{field_name}_simple_val'] = forms.CharField(label="Simple Value", required=False)
        self.fields[f'{field_name}_composed_val'] = forms.CharField(label="Composed Value", required=False)
        self.fields[f'{field_name}_null_val'] = forms.CharField(label="Null Value", required=False)

    def add_value_fields_to(self, component, field_name):
        form_row_1 = Div(css_class='form-row')
        form_row_1.append(Field(f'{field_name}_simple_val', wrapper_class=f'col-md-6'))
        form_row_1.append(Div(HTML('<div class="alert alert-info">'
                                   'If you want to display a single value from the result, '
                                   'enter its key here. This field is ignored if the "Composed Value" field is set.'
                                   '</div>'), css_class='col-md-6'))
        component.append(form_row_1)

        form_row_2 = Div(css_class='form-row')
        form_row_2.append(Field(f'{field_name}_composed_val', wrapper_class=f'col-md-6'))
        form_row_2.append(Div(HTML('<div class="alert alert-info">'
                                   'If you want to display multiple values from the result, you'
                                   'can enter a string format here. The format string can be composed according to'
                                   'the Python string format syntax.'
                                   '</div>'), css_class='col-md-6'))
        component.append(form_row_2)

        form_row_3 = Div(css_class='form-row')
        form_row_3.append(Field(f'{field_name}_null_val', wrapper_class=f'col-md-6'))
        form_row_3.append(Div(HTML('<div class="alert alert-info">'
                                   'If there is no value for the given key, this value will be displayed.'
                                   '</div>'), css_class='col-md-6'))
        component.append(form_row_3)

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = "POST"
        helper.layout = layout = Layout()

        tabs = TabHolder(css_id='id_tabs')
        for tab_conf in self.render_configuration:
            tab = Tab(tab_conf["field_label"], css_id=tab_conf["field_name"])
            self.add_value_fields_to(tab, tab_conf["field_name"])
            tabs.append(tab)

        layout.append(tabs)

        return helper


class FilteredListWidget(s2forms.Select2MultipleWidget):
    """Widget to display a multi select2 dropdown for list configurations. """

    search_fields = [
        'list_name__icontains'
    ]


class MyTestForm(forms.Form):

    format_field = forms.CharField(label='Format', max_length=100)
    format_field.widget.attrs['class'] = 'form-control'

    dropdown_field = forms.MultipleChoiceField(label='Dropdown',
                                               choices=[('1', 'One'), ('2', 'Two'), ('3', 'Three'), ('4', 'Four')],
                                               widget=FilteredListWidget(attrs={'data-minimum-input-length': 0}))
