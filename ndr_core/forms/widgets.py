"""Widgets for crispy forms. """
from crispy_forms.layout import BaseInput
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_select2 import forms as s2forms
from ndr_core.ndr_helpers import get_search_field_config


class CSVTextEditorWidget(forms.Textarea):
    """Creates a text area for crispy forms. """

    instance = None
    def __init__(self, attrs=None):
        """Initializes the widget. """
        self.instance = attrs.get('instance', None)
        super().__init__()

    class Media:
        """Add the required media for the widget. """
        css = {
            'all': ('ndr_core/plugins/tabulator/css/tabulator.min.css',)
        }
        js = ('ndr_core/plugins/tabulator/js/tabulator.min.js',)

    def render(self, name, value, attrs=None, renderer=None):
        """Renders the widget. """
        if self.instance is None:
            return super().render(name, value, attrs, renderer)

        ajax_url = reverse('ndr_core:get_field_choices', kwargs={'field_name': self.instance.pk})
        header_url = reverse('ndr_core:get_field_header', kwargs={'field_name': self.instance.pk})

        script = f"""
<script>
    $.ajax({{url: "{header_url}", success: function(result){{
        let header = result;
        header[header.length -1]['cellClick'] = function(e, cell){{
            if(confirm('Are you sure you want to delete this entry?')){{
                cell.getRow().delete();
            }}
        }};
        
        var data_count = 0;
        var table = new Tabulator("#{name}-table", {{
            ajaxURL: "{ajax_url}",
            index: "key",
            movableRows: true,
            addRowPos: "bottom",
            layout: "fitDataFill",
            height: "311px",
            columns: result
        }});
        
        table.on("dataLoaded", function(data){{
            data_count = data.length;
        }});
        
        document.getElementById("add-row").addEventListener("click", function(){{
            table.addRow({{'key': data_count}});
            data_count++;
        }});
        
    }}}});
    
</script>"""
        html = (f"""
        <button class="btn btn-sm btn-secondary" type="button" id="add-row" >Add Row</button>
        <div id="{name}-table"></div>
        {script}
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


class FilteredListWidget(s2forms.Select2MultipleWidget):
    """Widget to display a multi select2 dropdown for list configurations. """

    search_fields = [
        'list_name__icontains'
    ]
