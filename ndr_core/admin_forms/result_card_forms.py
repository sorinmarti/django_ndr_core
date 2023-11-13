"""Forms for the result card configuration. """
from django_select2 import forms as s2forms
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field, Row, Column, Submit, Button
from django import forms

from ndr_core.models import NdrCoreResultField


class SearchConfigurationResultEditForm(forms.Form):
    """Form to create or edit a search configuration result card. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for result_field_conf_row in range(20):
            required = False
            if result_field_conf_row == 0:
                required = True

            result_field = forms.ModelChoiceField(queryset=NdrCoreResultField.objects.all(),
                                                  required=required, help_text="")
            row_field = forms.IntegerField(required=required,
                                           help_text="")
            column_field = forms.IntegerField(required=required,
                                              help_text="")
            size_field = forms.IntegerField(required=required, help_text="")

            self.fields[f'result_field_{result_field_conf_row}'] = result_field
            self.fields[f'row_field_{result_field_conf_row}'] = row_field
            self.fields[f'column_field_{result_field_conf_row}'] = column_field
            self.fields[f'size_field_{result_field_conf_row}'] = size_field

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Div(css_class='form-row', css_id='result_field_config_title_row')
        form_row.append(Div(HTML('Result Field'), css_class='col-md-6'))
        form_row.append(Div(HTML('Row (1-?)'), css_class='col-md-2'))
        form_row.append(Div(HTML('Column (1-12)'), css_class='col-md-2'))
        form_row.append(Div(HTML('Size (1-12)'), css_class='col-md-2'))
        layout.append(form_row)

        for row in range(20):
            form_row = Div(css_class='form-row',
                           css_id=f'result_field_config_row_{row}')
            form_field_result_field = Field(f'result_field_{row}',
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

            form_row.append(form_field_result_field)
            form_row.append(form_field_row_field)
            form_row.append(form_field_column_field)
            form_row.append(form_field_size_field)

            layout.append(form_row)

        helper.form_show_labels = False

        form_row = Row(
            Column(HTML('<img id="preview_result_card_image" />'), css_class='col-md-12'),
            css_class='form-row'
        )
        layout.append(form_row)

        helper.add_input(Submit('submit', 'Update Result Configuration'))
        helper.add_input(Button('add_row', 'Add Row', css_class='btn btn-secondary'))
        helper.add_input(Button('remove_row', 'Remove Row', css_class='btn btn-secondary'))

        return helper


class FilteredListWidget(s2forms.Select2MultipleWidget):
    """Widget to display a multi select2 dropdown for list configurations. """

    result_fields = [
        'list_name__icontains'
    ]


class ResultDisplayConfigurationForm(forms.Form):
    """Form to create or edit a result display configuration. """

    def __init__(self, *args, **kwargs):
        """Initialises all needed form fields."""
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        helper.layout = layout = Layout()
        tabs = TabHolder(css_id="id_tabs")
        tab = Tab("label", css_id='tab_conf["field_name"]')
        tabs.append(tab)
        layout.append(tabs)
        return helper
