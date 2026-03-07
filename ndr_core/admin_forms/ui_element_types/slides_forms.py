"""Forms for Slides UI Element type."""
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms
from django.forms import inlineformset_factory

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUIElement, NdrCoreUiElementItem
from .base_forms import BaseUIElementForm, ImageChoiceField


class SlideItemForm(forms.ModelForm):
    """Form for a single slide item."""

    slide_image = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        label='Slide Image'
    )

    class Meta:
        model = NdrCoreUiElementItem
        fields = []  # We handle fields manually

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Import here to avoid circular imports
        from ndr_core.models import NdrCoreImage
        from .base_forms import ImagePickerWidget

        # Set up image field with custom widget
        self.fields['slide_image'] = forms.ModelChoiceField(
            queryset=NdrCoreImage.objects.filter(image_active=True).order_by('-uploaded_at'),
            required=False,
            label='Slide Image',
            widget=ImagePickerWidget()
        )

        # Populate initial value if editing
        if self.instance and self.instance.pk:
            self.fields['slide_image'].initial = self.instance.ndr_image

    def save(self, commit=True):
        """Save the slide item."""
        instance = super().save(commit=False)
        instance.ndr_image = self.cleaned_data.get('slide_image')

        if commit:
            instance.save()
        return instance


# Create the formset
SlidesItemFormSet = inlineformset_factory(
    NdrCoreUIElement,
    NdrCoreUiElementItem,
    form=SlideItemForm,
    extra=3,  # Show 3 empty forms by default
    max_num=20,  # Maximum 20 slides
    can_delete=True,
    can_order=True
)


class SlidesForm(BaseUIElementForm):
    """Form for Slides UI Element - displays multiple images in a slideshow."""

    # Fields for slideshow options
    show_indicators = forms.BooleanField(
        required=False,
        label='Show Indicators',
        help_text='Display slide indicators (dots) at the bottom'
    )
    autoplay = forms.BooleanField(
        required=False,
        label='Autoplay',
        help_text='Automatically advance slides'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ui_element_type='slides', **kwargs)

        # Populate options if editing
        if self.instance and self.instance.pk:
            self.fields['show_indicators'].initial = self.instance.show_indicators
            self.fields['autoplay'].initial = self.instance.autoplay

    def save(self, commit=True):
        """Save the Slides UI Element."""
        instance = super().save(commit=False)
        instance.show_indicators = self.cleaned_data.get('show_indicators', False)
        instance.autoplay = self.cleaned_data.get('autoplay', False)

        if commit:
            instance.save()
        return instance

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = self.get_base_helper()
        layout = helper.layout

        # Info section
        self.add_info_section(
            layout,
            'Slideshow UI Element',
            'A Slideshow displays multiple images that users can navigate through. '
            'You can add up to 20 slides. Configure options like indicators and autoplay below.'
        )

        # Name and Label fields
        self.add_field_row(layout, 'name', 'label', col_class='col-md-6')

        # Options section
        layout.append(Row(
            Column(HTML('<h5 class="mt-3 mb-3">Slideshow Options</h5>'), css_class='col-12'),
            css_class='row g-2'
        ))

        self.add_field_row(layout, 'show_indicators', 'autoplay', col_class='col-md-3')

        return helper


class SlidesCreateForm(SlidesForm):
    """Form to create a new Slides UI Element."""

    @property
    def helper(self):
        helper = super().helper
        # Note: Items section is added in the template via formset
        helper.layout.append(get_form_buttons('Create Slideshow'))
        return helper


class SlidesEditForm(SlidesForm):
    """Form to edit an existing Slides UI Element."""

    def __init__(self, *args, **kwargs):
        # Store original name for rename detection
        self._original_name = kwargs['instance'].name if 'instance' in kwargs else None
        super().__init__(*args, **kwargs)

        # Update help text to indicate renaming is possible
        self.fields['name'].help_text = 'Unique slug/identifier. Can be changed - renaming will preserve all settings.'

    def save(self, commit=True):
        """Save with special handling for name changes (PK changes)."""
        # Check if name was changed
        name_changed = self._original_name and self._original_name != self.cleaned_data.get('name')

        if name_changed and commit:
            # Handle rename: Create new instance and mark for old instance deletion
            # The formset will handle copying items to the new instance
            old_instance = NdrCoreUIElement.objects.get(name=self._original_name)

            # Call parent save to create new instance with new name
            new_instance = super().save(commit=True)

            # Store reference to old instance for view to handle deletion after formset save
            new_instance._old_instance_to_delete = old_instance

            return new_instance
        else:
            # Normal save
            return super().save(commit=commit)

    @property
    def helper(self):
        helper = super().helper
        # Note: Items section is added in the template via formset
        helper.layout.append(get_form_buttons('Save Slideshow'))
        return helper
