"""Forms for Video UI Element type."""
import re
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUIElement, NdrCoreUiElementItem
from .base_forms import BaseUIElementForm


class VideoForm(BaseUIElementForm):
    """Form for Video UI Element - embed videos from various providers."""

    # Video provider choices
    VIDEO_PROVIDERS = [
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
        ('switchtube', 'SwitchTube'),
    ]

    # Video-specific fields (single item)
    provider = forms.ChoiceField(
        choices=VIDEO_PROVIDERS,
        required=True,
        label='Video Provider',
        help_text='Select the video hosting platform'
    )
    video_id = forms.CharField(
        max_length=255,
        required=True,
        label='Video ID or URL',
        help_text='Enter the video ID or full URL (e.g., dQw4w9WgXcQ for YouTube)'
    )
    title = forms.CharField(
        max_length=100,
        required=False,
        label='Title',
        help_text='Optional video title'
    )
    text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Description',
        help_text='Optional video description'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ui_element_type='video', **kwargs)

    def clean_video_id(self):
        """Extract video ID from URL or return as-is if already an ID."""
        video_input = self.cleaned_data.get('video_id', '').strip()
        provider = self.cleaned_data.get('provider', '')

        if not video_input:
            return video_input

        # YouTube ID extraction
        if provider == 'youtube':
            # Pattern 1: https://www.youtube.com/watch?v=VIDEO_ID
            match = re.search(r'(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]+)', video_input)
            if match:
                return match.group(1)

            # Pattern 2: https://youtu.be/VIDEO_ID
            match = re.search(r'(?:youtu\.be/)([a-zA-Z0-9_-]+)', video_input)
            if match:
                return match.group(1)

            # Pattern 3: https://www.youtube.com/embed/VIDEO_ID
            match = re.search(r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]+)', video_input)
            if match:
                return match.group(1)

            # If no match, assume it's already an ID
            return video_input

        # Vimeo ID extraction
        elif provider == 'vimeo':
            # Pattern: https://vimeo.com/VIDEO_ID
            match = re.search(r'(?:vimeo\.com/)(\d+)', video_input)
            if match:
                return match.group(1)

            # If no match, assume it's already an ID
            return video_input

        # SwitchTube ID extraction
        elif provider == 'switchtube':
            # Pattern: https://tube.switch.ch/videos/VIDEO_ID or similar
            match = re.search(r'(?:tube\.switch\.ch/(?:videos|embed)/)([a-zA-Z0-9_-]+)', video_input)
            if match:
                return match.group(1)

            # If no match, assume it's already an ID
            return video_input

        return video_input

    def save(self, commit=True):
        """Save the Video UI Element and its single item."""
        instance = super().save(commit=commit)

        if commit:
            # Delete existing items and create a new one
            instance.ndrcoreuielementitem_set.all().delete()

            # Create the video item
            NdrCoreUiElementItem.objects.create(
                belongs_to=instance,
                order_idx=0,
                provider=self.cleaned_data.get('provider', ''),
                object_id=self.cleaned_data.get('video_id', ''),
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
            'Video UI Element',
            'Embed videos from YouTube, Vimeo, or SwitchTube. Select the provider and enter the video ID or URL. '
            'The video will be displayed in a responsive player.'
        )

        # Name and Label fields
        self.add_field_row(layout, 'name', 'label', col_class='col-md-6')

        # Video content section
        layout.append(Row(
            Column(HTML('<h5 class="mt-3 mb-3">Video Configuration</h5>'), css_class='col-12'),
            css_class='row g-2'
        ))

        self.add_field_row(layout, 'provider', col_class='col-md-6')
        self.add_field_row(layout, 'video_id', col_class='col-md-6')
        self.add_field_row(layout, 'title', col_class='col-md-6')
        self.add_field_row(layout, 'text', col_class='col-md-12')

        return helper


class VideoCreateForm(VideoForm):
    """Form to create a new Video UI Element."""

    @property
    def helper(self):
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Video'))
        return helper


class VideoEditForm(VideoForm):
    """Form to edit an existing Video UI Element."""

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
                item = items[0]  # Video only has one item
                self.fields['provider'].initial = item.provider
                self.fields['video_id'].initial = item.object_id
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
        helper.layout.append(get_form_buttons('Save Video'))
        return helper
