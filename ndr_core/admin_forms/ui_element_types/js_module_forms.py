"""Forms for JavaScript Module UI Element type."""
from django import forms
from crispy_forms.layout import Layout, Row, Column, HTML
from .base_forms import BaseUIElementForm
from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUIElement, NdrCoreUiElementItem


class JSModuleForm(BaseUIElementForm):
    """Base form for JavaScript Module UI Element."""

    # Primary upload method: Module package (zip)
    js_module_package = forms.FileField(
        required=False,
        label='Module Package (ZIP)',
        help_text='Upload a zip file with structure: static/ (JS/CSS files), media/ (images/data files), config.json'
    )

    # Module configuration (auto-populated from config.json or manual)
    js_module_config = forms.JSONField(
        required=False,
        initial=dict,
        label='Module Configuration',
        widget=forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
        help_text='Auto-populated from package config.json or enter manually for CDN-only modules.'
    )

    class Meta:
        model = NdrCoreUIElement
        fields = ['name', 'label']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ui_element_type='js_module', **kwargs)

        # Load existing item data if editing
        if self.instance and self.instance.pk:
            try:
                item = self.instance.ndrcoreuielementitem_set.first()
                if item:
                    self.initial['js_module_config'] = item.js_module_config
            except NdrCoreUiElementItem.DoesNotExist:
                pass

    def clean_js_module_config(self):
        """Validate JSON configuration structure."""
        config = self.cleaned_data.get('js_module_config', {})

        if not isinstance(config, dict):
            raise forms.ValidationError('Configuration must be a JSON object')

        # Validate structure (optional but helpful)
        if 'scripts' in config and not isinstance(config['scripts'], list):
            raise forms.ValidationError('scripts must be an array')

        if 'styles' in config and not isinstance(config['styles'], list):
            raise forms.ValidationError('styles must be an array')

        return config

    def save(self, commit=True):
        """Save the UI element and create/update the module item."""
        instance = super().save(commit=commit)

        if commit:
            # Delete existing items
            instance.ndrcoreuielementitem_set.all().delete()

            # Handle module package upload and extraction
            package_file = self.cleaned_data.get('js_module_package')
            module_config = self.cleaned_data.get('js_module_config', {})

            if package_file:
                # Extract package and get auto-populated config
                from ndr_core.js_module_handler import extract_module_package

                extracted_config = extract_module_package(
                    package_file,
                    instance.name,
                    ''  # module_name_hint not needed, will use instance.name
                )

                # Use extracted config if no manual config provided
                if not module_config:
                    module_config = extracted_config.get('config', {})

                # Create item with package reference
                NdrCoreUiElementItem.objects.create(
                    belongs_to=instance,
                    order_idx=0,
                    js_module_config=module_config,
                    js_module_package=package_file,
                    js_module_extracted=True,
                    title=f"JS Module: {instance.name}"
                )
            else:
                # Manual configuration (CDN-based modules)
                NdrCoreUiElementItem.objects.create(
                    belongs_to=instance,
                    order_idx=0,
                    js_module_config=module_config,
                    js_module_extracted=False,
                    title=f"JS Module: {instance.name}"
                )

        return instance

    @property
    def helper(self):
        """Create form layout using crispy forms."""
        helper = self.get_base_helper()
        layout = helper.layout

        # Info section
        self.add_info_section(
            layout,
            'JavaScript Module',
            'Create a custom JavaScript visualization or interactive element. '
            'Upload a package with assets or use external CDN libraries (D3.js, Chart.js, Plotly).'
        )

        # Name and Label fields (required)
        self.add_field_row(layout, 'name', 'label', col_class='col-md-6')

        # Configuration section
        layout.append(Row(
            Column(HTML('<h5 class="mt-3 mb-3">Module Configuration</h5>'), css_class='col-12'),
            css_class='row g-2'
        ))

        # Package upload
        self.add_field_row(layout, 'js_module_package', col_class='col-md-12')

        # Configuration JSON
        self.add_field_row(layout, 'js_module_config', col_class='col-md-12')

        # Example configuration
        layout.append(
            Row(
                Column(
                    HTML('''
                    <div class="alert alert-info">
                        <strong>Example Configuration:</strong>
                        <pre>{
  "scripts": ["https://d3js.org/d3.v7.min.js"],
  "styles": ["https://example.com/style.css"],
  "constructor": "MyVisualization",
  "options": {
    "dataUrl": "/media/data.json",
    "width": 800,
    "height": 600
  }
}</pre>
                    </div>
                    '''),
                    css_class='col-md-12'
                ),
                css_class='row g-2'
            )
        )

        return helper


class JSModuleCreateForm(JSModuleForm):
    """Form for creating a new JavaScript Module UI Element."""

    @property
    def helper(self):
        helper = super().helper
        helper.layout.append(get_form_buttons('Create JS Module'))
        return helper


class JSModuleEditForm(JSModuleForm):
    """Form for editing an existing JavaScript Module UI Element."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Track original name for rename detection
        if self.instance and self.instance.pk:
            self._original_name = self.instance.name

    def save(self, commit=True):
        """Handle rename if name changed."""
        if hasattr(self, '_original_name') and self._original_name != self.cleaned_data['name']:
            # Name changed - delete old instance after creating new one
            old_instance = NdrCoreUIElement.objects.get(pk=self._original_name)

            # Create new instance
            self.instance.pk = self.cleaned_data['name']
            self.instance._state.adding = True
            instance = super().save(commit=commit)

            # Delete old instance
            old_instance.delete()

            return instance
        else:
            # Normal save
            return super().save(commit=commit)

    @property
    def helper(self):
        helper = super().helper
        helper.layout.append(get_form_buttons('Save JS Module', include_save_and_continue=True))
        return helper
