import django.forms as forms
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML


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
