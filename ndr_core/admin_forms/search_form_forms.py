"""Form to create or edit a search configuration search form. """
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field, Row, Column, Submit, Button
from django import forms

from ndr_core.models import NdrCoreSearchField


class SearchConfigurationFormEditForm(forms.Form):
    """Form to create or edit a search configuration search form. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['is_simple_search'] = forms.BooleanField(required=False, help_text="")

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

        form_row = Div(css_class='row g-2', css_id='search_field_config_title_row')
        form_row.append(Div(HTML('Search Field'), css_class='col-md-6'))
        form_row.append(Div(HTML('Row (1-?)'), css_class='col-md-2'))
        form_row.append(Div(HTML('Column (1-12)'), css_class='col-md-2'))
        form_row.append(Div(HTML('Size (1-12)'), css_class='col-md-2'))
        layout.append(form_row)

        for row in range(20):
            form_row = Div(css_class='row g-2', css_id=f'search_field_config_row_{row}')
            form_field_search_field = Field(f'search_field_{row}',
                                            placeholder=f"Search Field {row+1}",
                                            wrapper_class='col-md-6')
            form_field_row_field = Field(f'row_field_{row}',
                                         placeholder="Row",
                                         wrapper_class='col-md-2')
            form_field_column_field = Field(f'column_field_{row}',
                                            placeholder="Column",
                                            wrapper_class='col-md-2')
            form_field_size_field = Field(f'size_field_{row}',
                                          placeholder="Size",
                                          wrapper_class='col-md-2')

            form_row.append(form_field_search_field)
            form_row.append(form_field_row_field)
            form_row.append(form_field_column_field)
            form_row.append(form_field_size_field)

            layout.append(form_row)

        helper.form_show_labels = False

        form_row = Row(
            Column(HTML('<img id="preview_search_form_image" />'), css_class='col-md-9'),
            Column(
                Div(Button('add_row', 'Add Row',
                           css_class='btn btn-sm btn-secondary float-right ml-3'),
                    Button('remove_row', 'Remove Row',
                           css_class='btn btn-sm btn-secondary float-right ml-3'),
                    css_class='display-flex'),
                css_class='col-md-3'),
            css_class='row g-2'
        )
        layout.append(form_row)

        helper.add_input(Submit('submit', 'Update Search Form Configuration'))

        return helper
