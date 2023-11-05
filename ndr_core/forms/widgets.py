from crispy_forms.layout import BaseInput
from django import forms
from django.utils.safestring import mark_safe
from ndr_core.ndr_helpers import get_search_field_config
from django_select2 import forms as s2forms


class BootstrapSwitchWidget(forms.Widget):

    def render(self, name, value, attrs=None, renderer=None):
        selected = ""
        if value:
            selected = "checked"
        html = '<div class="custom-control custom-switch">' \
               f'  <input type="checkbox" {selected} name="{name}" class="custom-control-input" id="{attrs["id"]}">' \
               f'  <label class="custom-control-label small" for="{attrs["id"]}">{ self.attrs.get("label", "") }</label>' \
               '</div>'
        return mark_safe(html)


class SwitchGroupWidget(forms.Widget):

    def render(self, name, value, attrs=None, renderer=None):
        html = '<div class="form-group">'
        for x in range(3):
            html += '<div class="custom-control custom-switch">' \
                   f'  <input type="checkbox" name="{name}" class="custom-control-input" id="{attrs["id"]}{x}">' \
                   f'  <label class="custom-control-label small" for="{attrs["id"]}{x}">{ self.attrs.get("label", "") }</label>' \
                   '</div>'
        html += '</div>'
        return mark_safe(html)


class CustomRange(forms.TextInput):

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


class FilteredListWidget(s2forms.Select2MultipleWidget):
    """Widget to display a multi select2 dropdown for list configurations. """

    search_fields = [
        'list_name__icontains'
    ]
