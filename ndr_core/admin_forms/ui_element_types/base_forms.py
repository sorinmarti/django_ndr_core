"""Base forms and widgets for UI Element types."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, HTML
from django import forms
from django.forms.widgets import Select

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreImage, NdrCoreUIElement


class ImagePickerWidget(Select):
    """Widget that displays images using the image-picker plugin."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'image-picker show_html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            try:
                # Extract the actual value from ModelChoiceIteratorValue if needed
                actual_value = value.value if hasattr(value, 'value') else value

                # Skip if it's not a valid ID
                if actual_value and actual_value != '':
                    image = NdrCoreImage.objects.get(pk=actual_value)
                    option['attrs']['data-img-src'] = image.image.url
                    option['attrs']['data-img-label'] = image.alt_text or 'Image'
            except (NdrCoreImage.DoesNotExist, ValueError, TypeError):
                pass
        return option


class ImageChoiceField(forms.ModelChoiceField):
    """Used to display images in a select field with thumbnails."""

    widget = ImagePickerWidget

    def label_from_instance(self, obj):
        return obj.alt_text or 'Image'

    def to_python(self, value):
        """Convert the value to a model instance."""
        if value in self.empty_values:
            return None

        # Handle ModelChoiceIteratorValue objects
        if hasattr(value, 'value'):
            value = value.value

        try:
            # Convert string ID to integer and get the instance
            if isinstance(value, str) and value.isdigit():
                value = int(value)

            # If it's already a model instance, return it
            if isinstance(value, self.queryset.model):
                return value

            key = self.to_field_name or 'pk'
            value = self.queryset.get(**{key: value})
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise forms.ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
            )
        return value


class BaseUIElementForm(forms.ModelForm):
    """Base form for all UI Element types."""

    class Meta:
        model = NdrCoreUIElement
        fields = ['name', 'label']

    def __init__(self, *args, ui_element_type=None, **kwargs):
        """
        Initialize the form.

        Args:
            ui_element_type: The UI element type (e.g., 'card', 'slides')
        """
        super().__init__(*args, **kwargs)
        self.ui_element_type = ui_element_type

    def save(self, commit=True):
        """Save the UI Element with the specified type."""
        instance = super().save(commit=False)
        if self.ui_element_type:
            instance.type = self.ui_element_type
        if commit:
            instance.save()
        return instance

    def get_image_queryset(self):
        """Get queryset for image selection."""
        return NdrCoreImage.objects.filter(image_active=True).order_by('-uploaded_at')

    def create_image_field(self, label='Image', required=False, help_text=None):
        """Create an image choice field with image picker widget."""
        return ImageChoiceField(
            queryset=self.get_image_queryset(),
            required=required,
            label=label,
            help_text=help_text
        )

    def get_base_helper(self, button_text='Save'):
        """Get base form helper with common configuration."""
        helper = FormHelper()
        helper.form_method = "POST"
        helper.layout = Layout()
        return helper

    def add_info_section(self, layout, title, description):
        """Add an info section to the layout."""
        layout.append(Row(
            Column(Div(HTML(f'''
                <div class="alert alert-info">
                    <strong>{title}</strong>
                    <p class="mb-0">{description}</p>
                </div>
            ''')), css_class='col-12'),
            css_class='form-row mb-3'
        ))

    def add_field_row(self, layout, *fields, col_class='col-md-6'):
        """Add a row with fields to the layout."""
        columns = [Column(field, css_class=f'form-group {col_class} mb-0') for field in fields]
        layout.append(Row(*columns, css_class='row g-2'))
