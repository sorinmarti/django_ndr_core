from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe

from ndr_core.ndr_helpers import get_search_field_config


class BootstrapSwitchWidget(forms.Widget):

    def render(self, name, value, attrs=None, renderer=None):
        selecteed = ""
        if value:
            selecteed = "checked"
        html = '<div class="custom-control custom-switch">' \
               f'  <input type="checkbox" {selecteed} name="{name}" class="custom-control-input" id="{attrs["id"]}">' \
               f'  <label class="custom-control-label small" for="{attrs["id"]}">{ self.attrs.get("label", "") }</label>' \
               '</div>'
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
