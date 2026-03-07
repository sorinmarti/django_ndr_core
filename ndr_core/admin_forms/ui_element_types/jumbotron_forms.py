"""Forms for Jumbotron UI Element type."""
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUIElement, NdrCoreUiElementItem
from .base_forms import BaseUIElementForm


class JumbotronForm(BaseUIElementForm):
    """Form for Jumbotron UI Element - large callout with background image and text."""

    # Jumbotron-specific fields (single item)
    background_image = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        label='Background Image',
        help_text='Select a background image for the jumbotron'
    )
    title = forms.CharField(
        max_length=100,
        required=False,
        label='Title',
        help_text='Jumbotron title'
    )
    text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label='Text',
        help_text='Jumbotron description text'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ui_element_type='jumbotron', **kwargs)

        # Set up image field with custom widget
        self.fields['background_image'] = self.create_image_field(
            label='Background Image',
            help_text='Select a background image for the jumbotron'
        )

    def save(self, commit=True):
        """Save the Jumbotron UI Element and its single item."""
        instance = super().save(commit=commit)

        if commit:
            # Delete existing items and create a new one
            instance.ndrcoreuielementitem_set.all().delete()

            # Create the jumbotron item
            NdrCoreUiElementItem.objects.create(
                belongs_to=instance,
                order_idx=0,
                ndr_image=self.cleaned_data.get('background_image'),
                title=self.cleaned_data.get('title', ''),
                text=self.cleaned_data.get('text', '')
            )

        return instance

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = self.get_base_helper()
        layout = helper.layout

        # Info section
        self.add_info_section(
            layout,
            'Jumbotron UI Element',
            'A Jumbotron is a large callout area that can feature a background image, '
            'title, and descriptive text. Great for hero sections and important announcements.'
        )

        # Name and Label fields
        self.add_field_row(layout, 'name', 'label', col_class='col-md-6')

        # Jumbotron content section
        layout.append(Row(
            Column(HTML('<h5 class="mt-3 mb-3">Jumbotron Content</h5>'), css_class='col-12'),
            css_class='row g-2'
        ))

        self.add_field_row(layout, 'background_image', col_class='col-md-6')
        self.add_field_row(layout, 'title', col_class='col-md-6')
        self.add_field_row(layout, 'text', col_class='col-md-12')

        return helper


class JumbotronCreateForm(JumbotronForm):
    """Form to create a new Jumbotron UI Element."""

    @property
    def helper(self):
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Jumbotron'))
        return helper


class JumbotronEditForm(JumbotronForm):
    """Form to edit an existing Jumbotron UI Element."""

    def __init__(self, *args, **kwargs):
        # Store original name for rename detection
        self._original_name = kwargs['instance'].name if 'instance' in kwargs else None
        super().__init__(*args, **kwargs)

        # Update help text to indicate renaming is possible
        self.fields['name'].help_text = 'Unique slug/identifier. Can be changed - renaming will preserve all settings.'

        # Populate form fields with existing item data
        if self.instance and self.instance.pk:
            items = self.instance.items()
            if items:
                item = items[0]  # Jumbotron only has one item
                self.fields['background_image'].initial = item.ndr_image
                self.fields['title'].initial = item.title
                self.fields['text'].initial = item.text

    def save(self, commit=True):
        """Save with special handling for name changes (PK changes)."""
        # Check if name was changed
        name_changed = self._original_name and self._original_name != self.cleaned_data.get('name')

        if name_changed and commit:
            # Handle rename: The new instance will be created, we need to delete the old one
            old_instance = NdrCoreUIElement.objects.get(name=self._original_name)

            # Call parent save to create new instance with new name
            new_instance = super().save(commit=True)

            # Delete old instance (the new one already has the correct data from the form)
            old_instance.delete()

            return new_instance
        else:
            # Normal save
            return super().save(commit=commit)

    @property
    def helper(self):
        helper = super().helper
        helper.layout.append(get_form_buttons('Save Jumbotron'))
        return helper
