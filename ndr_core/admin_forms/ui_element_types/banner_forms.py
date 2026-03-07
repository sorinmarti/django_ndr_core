"""Forms for Banner UI Element type."""
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUIElement, NdrCoreUiElementItem
from .base_forms import BaseUIElementForm


class BannerForm(BaseUIElementForm):
    """Form for Banner UI Element - large image banner."""

    # Banner-specific fields (single item)
    banner_image = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        label='Banner Image',
        help_text='Select an image for the banner'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ui_element_type='banner', **kwargs)

        # Set up image field with custom widget
        self.fields['banner_image'] = self.create_image_field(
            label='Banner Image',
            help_text='Select an image for the banner'
        )

    def save(self, commit=True):
        """Save the Banner UI Element and its single item."""
        instance = super().save(commit=commit)

        if commit:
            # Delete existing items and create a new one
            instance.ndrcoreuielementitem_set.all().delete()

            # Create the banner item
            NdrCoreUiElementItem.objects.create(
                belongs_to=instance,
                order_idx=0,
                ndr_image=self.cleaned_data.get('banner_image')
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
            'Banner UI Element',
            'A Banner displays a large image that spans the full width of the content area. '
            'Perfect for headers, announcements, or visual separators.'
        )

        # Name and Label fields
        self.add_field_row(layout, 'name', 'label', col_class='col-md-6')

        # Banner content section
        layout.append(Row(
            Column(HTML('<h5 class="mt-3 mb-3">Banner Content</h5>'), css_class='col-12'),
            css_class='row g-2'
        ))

        self.add_field_row(layout, 'banner_image', col_class='col-md-6')

        return helper


class BannerCreateForm(BannerForm):
    """Form to create a new Banner UI Element."""

    @property
    def helper(self):
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Banner'))
        return helper


class BannerEditForm(BannerForm):
    """Form to edit an existing Banner UI Element."""

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
                item = items[0]  # Banner only has one item
                self.fields['banner_image'].initial = item.ndr_image

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
        helper.layout.append(get_form_buttons('Save Banner'))
        return helper
