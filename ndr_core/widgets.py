from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe


class CustomSelect(forms.Select):
    def __init__(self, attrs=None, choices=()):
        self.custom_attrs = {}
        super().__init__(attrs, choices)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        index = str(index) if subindex is None else "%s_%s" % (index, subindex)
        if attrs is None:
            attrs = {}
        option_attrs = self.build_attrs(self.attrs, attrs) if self.option_inherits_attrs else {}
        if selected:
            option_attrs.update(self.checked_attribute)
        if 'id' in option_attrs:
            option_attrs['id'] = self.id_for_label(option_attrs['id'], index)

        # setting the attributes here for the option
        if len(self.custom_attrs) > 0:
            if value in self.custom_attrs:
                custom_attr = self.custom_attrs[value]
                for k, v in custom_attr.items():
                    option_attrs.update({k: v})

        return {
            'name': name,
            'value': value,
            'label': label,
            'selected': selected,
            'index': index,
            'attrs': option_attrs,
            'type': self.input_type,
            'template_name': self.option_template_name,
        }

    def render(self, name, value, attrs=None, renderer=None):
        field_name = self.attrs["list_name"]
        if "placeholder" not in self.attrs:
            placeholder = f"Select {field_name}"
        else:
            placeholder = self.attrs["placeholder"]

        html = f'<select class="js-example-basic-multiple js-states form-control" name="{field_name}[]" multiple="multiple" id="{field_name}_select"></select>'
        inline_code = "  $(document).ready(function() {\n"\
            f"    $('#{field_name}_select').select2({{\n"\
            f"      placeholder: '{placeholder}',\n" \
            "      ajax: {\n"\
            f"        url: '{reverse('ndr_core_api:list_autocomplete', kwargs={'list_name': field_name})}',\n"\
            "        dataType: 'json',\n"\
            "        processResults: function (data) {\n"\
            "            return {\n"\
            "                results: data.map(function (item) {\n"\
            "                    return {id: item[0],\n"\
            "                             text: item[1]}\n"\
            "                })\n"\
            "            }\n"\
            "        }\n"\
            "      },\n"\
            "    allowClear: false\n"\
            "  });\n"\
            "});\n"\


        if "selection" in self.attrs:
            preselect_code = f"let {field_name}_select = $('#{field_name}_select');\n"
            preselect_values = self.attrs['selection']
            for val in preselect_values:
                preselect_code += "$.ajax({\n"\
                                  "  type: 'GET',\n"\
                                  f"  url: '{reverse('ndr_core_api:list_autocomplete_key_single', kwargs={'list_name': field_name, 'selected_value': val})}'\n"\
                                  "}).then(function (data) {\n"\
                                  "  var option = new Option(data[1], data[0], true, true);\n"\
                                  f"  {field_name}_select.append(option).trigger('change');\n"\
                                  f"  {field_name}_select.trigger({{\n"\
                                  "    type: 'select2:select',\n"\
                                  "    params: {\n"\
                                  "      data: data\n"\
                                  "    }\n"\
                                  "  });\n"\
                                  "});\n"

        return mark_safe(html + "<script>" + inline_code + preselect_code + "</script>")


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
