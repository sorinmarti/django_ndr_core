"""Widgets for crispy forms. """
from crispy_forms.helper import FormHelper
from crispy_forms.layout import BaseInput, Layout, Row, Column, HTML
from django import forms
from django.contrib.staticfiles import finders
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_select2 import forms as s2forms

from ndr_core.ndr_helpers import get_search_field_config
from django.template import Template, Context
from django.template import loader


class CSVTextEditorWidget(forms.Textarea):
    """Creates a text area for crispy forms. """

    instance = None
    type_field_id = None

    def __init__(self, attrs=None):
        """Initializes the widget. """
        self.instance = attrs.get('instance', None)
        self.type_field_id = attrs.get('type_field_id', None)

        super().__init__()

    class ImportCsvForm(forms.Form):
        """Form to import CSV data. """
        import_type = forms.ChoiceField(choices=[("csv", "CSV"), ("json", "JSON")],
                                        label="Import Type",
                                        help_text="Select the type of data you want to import.")

        csv_file = forms.FileField(label="File",
                                   help_text="Select a CSV or JSON file to import.")

        csv_delimiter = forms.CharField(max_length=3, initial=",",
                                        label="Delimiter",
                                        help_text="The delimiter used in the CSV file. Write 'TAB' for tabulator.")

        replace_data = forms.BooleanField(required=False,
                                          label="Replace existing data?",
                                          help_text="If checked, existing data will be replaced. "
                                                    "If not checked, new data will be appended.")

        @property
        def helper(self):
            """Creates and returns the form helper property."""
            helper = FormHelper()
            helper.form_method = "GET"
            layout = helper.layout = Layout()

            form_row = Row(
                Column('import_type', css_class='form-group col-6'),
                css_class='row g-2'
            )
            layout.append(form_row)

            form_row = Row(
                Column('csv_file', css_class='form-group col-12'),
                css_class='row g-2'
            )
            layout.append(form_row)

            form_row = Row(
                Column('csv_delimiter', css_class='form-group col-6'),
                Column('replace_data', css_class='form-group col-6'),
                css_class='row g-2'
            )
            layout.append(form_row)

            return helper

    class Media:
        """Add the required media for the widget. """
        css = {
            'all': ('ndr_core/plugins/tabulator/css/tabulator.min.css',)
        }
        js = ('ndr_core/plugins/tabulator/js/tabulator.min.js',)

    def render(self, name, value, attrs=None, renderer=None):
        """Renders the widget. """

        if self.instance is None:
            # New entry
            field_type = 0
            field_name = "create"
        else:
            field_type = self.instance.field_type
            field_name = self.instance.pk

        header_url = reverse('ndr_core:get_field_header', kwargs={'field_type': field_type})
        ajax_url = reverse('ndr_core:get_field_choices', kwargs={'field_name': field_name})

        file_path = finders.find("ndr_core/js/widgets/csv_text_editor_widget_template.js")
        with open(file_path, 'r') as file:
            content = file.read()
            script = content.replace('__header_url__', header_url)
            script = script.replace('__ajax_url__', ajax_url)
            script = script.replace('__name__', name)

        html = (f"""<div id="{name}-table"></div>
                    <textarea id="{name}" name="{name}" style="display: none;">{value}</textarea>
                    <div class="mt-1">
                        <button class="btn btn-sm btn-secondary" type="button" id="add-row">Add Row</button>
                        <button class="btn btn-sm btn-secondary" type="button" data-toggle="modal" data-target="#importCSVModal">Import Data</button>
                        <button class="btn btn-sm btn-secondary" type="button" data-toggle="modal" id="export-data">Export Data</button>
                        <button class="btn btn-sm btn-secondary" type="button" data-toggle="modal" id="clear-data">Clear Data</button>
                    </div>
                    <script>{script}</script>
                """)

        return mark_safe(html)


class BootstrapSwitchWidget(forms.Widget):
    """Creates a switch for crispy forms. """

    def render(self, name, value, attrs=None, renderer=None):
        selected = ""
        if value:
            selected = "checked"
        html = f"""
        <div class="custom-control custom-switch">
            <input type="checkbox" {selected} name="{name}" class="custom-control-input" id="{attrs["id"]}">
            <label class="custom-control-label small" for="{attrs["id"]}">{ self.attrs.get("label", "") }</label>
        </div>
        """
        return mark_safe(html)


class CustomRange(forms.TextInput):
    """Creates a range slider for crispy forms. """

    def render(self, name, value, attrs=None, renderer=None):
        config = get_search_field_config(name)

        lower_number = self.attrs["lower_number"]
        upper_number = self.attrs["upper_number"]

        html = '<div><range-selector\n'\
               f'    id="{name}RangeSlider" \n'\
               f'    min-range="{config["number-range"]["min_number"]}" \n'\
               f'    max-range="{config["number-range"]["max_number"]}" \n'\
               f'    preset-min="{lower_number}" \n'\
               f'    preset-max="{upper_number}" \n'\
               '    slider-color="#870437" \n'\
               '    slider-border-color="#DEE2E6" \n'\
               '    number-of-legend-items-to-show="5" \n'\
               '    inputs-for-labels />\n'\
               f'<input type="number" id="startRange_{name}" name="startRange_{name}" value="{lower_number}"/>\n'\
               f'<input type="number" id="endRange_{name}" name="endRange_{name}" value="{upper_number}"/></div>\n'

        inline_code = "window.addEventListener('range-changed', (e) => {\n"\
            "const data = e.detail;\n"\
            f"document.getElementById('startRange_{name}').value = data.minRangeValue;\n"\
            f"document.getElementById('endRange_{name}').value = data.maxRangeValue;\n"\
            "});"

        return mark_safe(html + "<script>" + inline_code + "</script>")


class NdrCoreFormSubmit(BaseInput):
    """Creates a submit button for crispy forms. """

    input_type = "submit"

    def __init__(self, *args, **kwargs):
        """Init the submit button. """
        self.field_classes = "btn btn-primary w-100"
        super().__init__(*args, **kwargs)


class NdrCoreFilterButton(HTML):
    """Creates a filter button with icon for crispy forms. """

    def __init__(self, value, **kwargs):
        """Init the filter button. """
        button_html = f'''
            <button type="submit" name="filter_button" class="btn btn-primary align-self-start">
                <i class="fa-solid fa-filter"></i> {value}
            </button>
        '''
        super().__init__(mark_safe(button_html))


class NdrCoreClearButton(HTML):
    """Creates a clear button with icon for crispy forms. """

    def __init__(self, value, **kwargs):
        """Init the clear button. """
        button_html = f'''
            <button type="button" class="btn btn-secondary align-self-start" onclick="window.location.href = window.location.pathname;">
                <i class="fa-solid fa-eraser"></i> {value}
            </button>
        '''
        super().__init__(mark_safe(button_html))


class FilteredListWidget(s2forms.Select2MultipleWidget):
    """Widget to display a multi select2 dropdown for list configurations. """

    search_fields = [
        'list_name__icontains'
    ]
