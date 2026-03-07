"""Forms for Manifest Viewer UI Element type."""
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import (NdrCoreUIElement, NdrCoreUiElementItem,
                              NdrCoreManifestGroup)
from .base_forms import BaseUIElementForm


class ManifestViewerForm(BaseUIElementForm):
    """Form for Manifest Viewer UI Element - displays IIIF manifests."""

    # Manifest Viewer-specific fields (single item)
    manifest_group = forms.ModelChoiceField(
        queryset=NdrCoreManifestGroup.objects.all(),
        required=False,
        label='Manifest Group',
        help_text='Select a manifest group to display'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ui_element_type='manifest_viewer', **kwargs)

    def save(self, commit=True):
        """Save the Manifest Viewer UI Element and its single item."""
        instance = super().save(commit=commit)

        if commit:
            # Delete existing items and create a new one
            instance.ndrcoreuielementitem_set.all().delete()

            # Create the manifest viewer item
            NdrCoreUiElementItem.objects.create(
                belongs_to=instance,
                order_idx=0,
                manifest_group=self.cleaned_data.get('manifest_group')
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
            'Manifest Viewer UI Element',
            'A Manifest Viewer displays IIIF manifests (digital images/documents) '
            'using an interactive viewer. Select a manifest group to display.'
        )

        # Name and Label fields
        self.add_field_row(layout, 'name', 'label', col_class='col-md-6')

        # Manifest Viewer content section
        layout.append(Row(
            Column(HTML('<h5 class="mt-3 mb-3">Manifest Viewer Content</h5>'), css_class='col-12'),
            css_class='row g-2'
        ))

        self.add_field_row(layout, 'manifest_group', col_class='col-md-6')

        return helper


class ManifestViewerCreateForm(ManifestViewerForm):
    """Form to create a new Manifest Viewer UI Element."""

    @property
    def helper(self):
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Manifest Viewer'))
        return helper


class ManifestViewerEditForm(ManifestViewerForm):
    """Form to edit an existing Manifest Viewer UI Element."""

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
                item = items[0]  # Manifest Viewer only has one item
                self.fields['manifest_group'].initial = item.manifest_group

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
        helper.layout.append(get_form_buttons('Save Manifest Viewer'))
        return helper
