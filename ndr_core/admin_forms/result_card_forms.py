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
                required = False    # Hack for now

            result_field = forms.ModelChoiceField(queryset=NdrCoreResultField.objects.all().order_by('label'),
                                                  required=required, help_text="")
            row_field = forms.IntegerField(required=required,
                                           help_text="")
            column_field = forms.IntegerField(required=required,
                                              help_text="")
            row_span_field = forms.IntegerField(required=required,
                                                help_text="")
            column_span_field = forms.IntegerField(required=required,
                                                   help_text="")

            self.fields[f'result_field_{result_field_conf_row}'] = result_field
            self.fields[f'row_field_{result_field_conf_row}'] = row_field
            self.fields[f'column_field_{result_field_conf_row}'] = column_field
            self.fields[f'row_span_field_{result_field_conf_row}'] = row_span_field
            self.fields[f'column_span_field_{result_field_conf_row}'] = column_span_field

            cpct_result_field = forms.ModelChoiceField(queryset=NdrCoreResultField.objects.all(),
                                                       required=required, help_text="")
            cpct_row_field = forms.IntegerField(required=required,
                                                help_text="")
            cpct_column_field = forms.IntegerField(required=required,
                                                   help_text="")
            cpct_row_span_field = forms.IntegerField(required=required,
                                                help_text="")
            cpct_column_span_field = forms.IntegerField(required=required,
                                                   help_text="")

            self.fields[f'cpct_result_field_{result_field_conf_row}'] = cpct_result_field
            self.fields[f'cpct_row_field_{result_field_conf_row}'] = cpct_row_field
            self.fields[f'cpct_column_field_{result_field_conf_row}'] = cpct_column_field
            self.fields[f'cpct_row_span_field_{result_field_conf_row}'] = cpct_row_span_field
            self.fields[f'cpct_column_span_field_{result_field_conf_row}'] = cpct_column_span_field

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        tab_holder = TabHolder(css_id='result_card_tabs')
        tab = Tab('Result Card')
        cpct_tab = Tab('Compact Result Card')

        form_row = Div(css_class='row g-2', css_id='result_field_config_title_row')
        form_row.append(Div(HTML('Result Field'), css_class='col-md-6'))
        form_row.append(Div(HTML('Row'), css_class='col-md-2'))
        form_row.append(Div(HTML('Col'), css_class='col-md-1'))
        form_row.append(Div(HTML('Width'), css_class='col-md-2'))
        form_row.append(Div(HTML('Height'), css_class='col-md-1'))
        tab.append(form_row)

        form_row = Div(css_class='row g-2', css_id='cpct_result_field_config_title_row')
        form_row.append(Div(HTML('Compact Result Field'), css_class='col-md-6'))
        form_row.append(Div(HTML('Row'), css_class='col-md-2'))
        form_row.append(Div(HTML('Col'), css_class='col-md-1'))
        form_row.append(Div(HTML('Width'), css_class='col-md-2'))
        form_row.append(Div(HTML('Height'), css_class='col-md-1'))
        cpct_tab.append(form_row)

        for row in range(20):
            form_row = Div(css_class='row g-2',
                           css_id=f'result_field_config_row_{row}')
            cpct_form_row = Div(css_class='row g-2',
                                css_id=f'cpct_result_field_config_row_{row}')

            form_field_result_field = Field(f'result_field_{row}',
                                            placeholder=f"Search Field {row+1}",
                                            wrapper_class='col-md-6')
            cpct_form_field_result_field = Field(f'cpct_result_field_{row}',
                                                 placeholder=f"Search Field {row+1}",
                                                 wrapper_class='col-md-6')

            form_field_row_field = Field(f'row_field_{row}',
                                         placeholder="Row",
                                         wrapper_class='col-md-2')
            cpct_form_field_row_field = Field(f'cpct_row_field_{row}',
                                              placeholder="Row",
                                              wrapper_class='col-md-2')

            form_field_column_field = Field(f'column_field_{row}',
                                            placeholder="Column",
                                            wrapper_class='col-md-1')
            cpct_form_field_column_field = Field(f'cpct_column_field_{row}',
                                                 placeholder="Column",
                                                 wrapper_class='col-md-1')

            form_field_row_span_field = Field(f'row_span_field_{row}',
                                          placeholder="Width",
                                          wrapper_class='col-md-2')
            cpct_form_field_row_span_field = Field(f'cpct_row_span_field_{row}',
                                               placeholder="Width",
                                               wrapper_class='col-md-2')

            form_field_column_span_field = Field(f'column_span_field_{row}',
                                              placeholder="Height",
                                              wrapper_class='col-md-1')
            cpct_form_field_column_span_field = Field(f'cpct_column_span_field_{row}',
                                                   placeholder="Height",
                                                   wrapper_class='col-md-1')

            form_row.append(form_field_result_field)
            form_row.append(form_field_row_field)
            form_row.append(form_field_column_field)
            form_row.append(form_field_column_span_field)
            form_row.append(form_field_row_span_field)

            cpct_form_row.append(cpct_form_field_result_field)
            cpct_form_row.append(cpct_form_field_row_field)
            cpct_form_row.append(cpct_form_field_column_field)
            cpct_form_row.append(cpct_form_field_column_span_field)
            cpct_form_row.append(cpct_form_field_row_span_field)

            tab.append(form_row)
            cpct_tab.append(cpct_form_row)

        form_row = Row(
            Column(HTML('<img id="preview_result_card_image" />'), css_class='col-md-9'),
            Column(
                Div(Button('add_row', 'Add Row',
                           css_class='btn btn-sm btn-secondary float-right ml-3'),
                    Button('remove_row', 'Remove Row',
                           css_class='btn btn-sm btn-secondary float-right ml-3'),
                    css_class='display-flex'),
                css_class='col-md-3'),
            css_class='row g-2'
        )
        tab.append(form_row)

        cpct_form_row = Row(
            Column(HTML('<img id="cpct_preview_result_card_image" />'), css_class='col-md-9'),
            Column(
                Div(Button('cpct_add_row', 'Add Row',
                           css_class='btn btn-sm btn-secondary float-right ml-3'),
                    Button('cpct_remove_row', 'Remove Row',
                           css_class='btn btn-sm btn-secondary float-right ml-3'),
                    css_class='display-flex'),
                css_class='col-md-3'),
            css_class='row g-2'
        )
        cpct_tab.append(cpct_form_row)

        tab_holder.append(tab)
        tab_holder.append(cpct_tab)

        layout.append(tab_holder)
        helper.form_show_labels = False

        helper.add_input(Submit('submit', 'Update Result Configuration'))

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
