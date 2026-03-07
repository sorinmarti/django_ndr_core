"""Forms for Team Members Grid UI Element type."""
import re
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django_ckeditor_5.widgets import CKEditor5Widget

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUIElement, NdrCoreUiElementItem
from .base_forms import BaseUIElementForm


def validate_orcid(value):
    """Validate ORCID format: XXXX-XXXX-XXXX-XXXX"""
    # Skip validation for empty values
    if not value or value.strip() == '':
        return

    if not re.match(r'^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$', value):
        raise ValidationError(
            'ORCID must be in format XXXX-XXXX-XXXX-XXXX (e.g., 0000-0002-1825-0097)'
        )


class TeamGridItemForm(forms.ModelForm):
    """Form for a single team member."""

    member_image = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        label='Profile Photo'
    )
    member_name = forms.CharField(
        max_length=100,
        required=False,
        label='Name',
        help_text='Full name of the team member',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    member_title = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        required=False,
        label='Title/Position',
        help_text='Job title, role, or position'
    )
    member_bio = forms.CharField(
        widget=CKEditor5Widget(config_name='page_editor'),
        required=False,
        label='Biography',
        help_text='Optional biography or description (supports rich text)'
    )
    member_website = forms.URLField(
        required=False,
        label='Website',
        help_text='Personal website or profile URL',
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    member_orcid = forms.CharField(
        max_length=19,
        required=False,
        label='ORCID',
        help_text='ORCID identifier (format: XXXX-XXXX-XXXX-XXXX)',
        validators=[validate_orcid],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0000-0000-0000-0000'})
    )

    class Meta:
        model = NdrCoreUiElementItem
        fields = []  # We handle fields manually

    def clean(self):
        """Validate that if any field is filled, required fields are provided."""
        cleaned_data = super().clean()

        # Check if any field has data (excluding DELETE)
        has_data = any([
            cleaned_data.get('member_name'),
            cleaned_data.get('member_title'),
            cleaned_data.get('member_bio'),
            cleaned_data.get('member_website'),
            cleaned_data.get('member_orcid'),
            cleaned_data.get('member_image'),
        ])

        # If form has data, ensure required fields are filled
        if has_data and not cleaned_data.get('DELETE'):
            if not cleaned_data.get('member_name'):
                self.add_error('member_name', 'Name is required for team members.')
            if not cleaned_data.get('member_title'):
                self.add_error('member_title', 'Title/Position is required for team members.')
            if not cleaned_data.get('member_orcid'):
                self.add_error('member_orcid', 'ORCID is required for team members.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Import here to avoid circular imports
        from ndr_core.models import NdrCoreImage
        from .base_forms import ImagePickerWidget

        # Set up image field with custom widget
        self.fields['member_image'] = forms.ModelChoiceField(
            queryset=NdrCoreImage.objects.filter(image_active=True).order_by('-uploaded_at'),
            required=False,
            label='Profile Photo',
            widget=ImagePickerWidget()
        )

        # Populate initial values if editing
        if self.instance and self.instance.pk:
            self.fields['member_image'].initial = self.instance.ndr_image
            self.fields['member_name'].initial = self.instance.title
            self.fields['member_title'].initial = self.instance.text
            self.fields['member_bio'].initial = self.instance.rich_text
            self.fields['member_website'].initial = self.instance.url
            self.fields['member_orcid'].initial = self.instance.object_id

    def save(self, commit=True):
        """Save the team member."""
        instance = super().save(commit=False)
        instance.ndr_image = self.cleaned_data.get('member_image')
        instance.title = self.cleaned_data.get('member_name', '')
        instance.text = self.cleaned_data.get('member_title', '')
        instance.rich_text = self.cleaned_data.get('member_bio', '')
        instance.url = self.cleaned_data.get('member_website', '')
        instance.object_id = self.cleaned_data.get('member_orcid', '')

        # Set order_idx from the formset's ORDER field
        # The formset provides ORDER as an integer when can_order=True
        order_value = self.cleaned_data.get('ORDER')
        if order_value is not None and order_value != '':
            instance.order_idx = int(order_value)
        elif not hasattr(instance, 'order_idx') or instance.order_idx is None:
            # If no order specified, we'll let the view handle it
            # Don't set a default here as it will be set by the formset
            instance.order_idx = 0

        if commit:
            instance.save()
        return instance


# Create the formset
TeamGridItemFormSet = inlineformset_factory(
    NdrCoreUIElement,
    NdrCoreUiElementItem,
    form=TeamGridItemForm,
    extra=1,  # Show 1 empty form by default
    max_num=50,  # Maximum 50 team members
    can_delete=True,
    can_order=True,
    validate_min=False,  # Don't require at least one item
    min_num=0  # Allow zero team members
)


class TeamGridForm(BaseUIElementForm):
    """Form for Team Members Grid UI Element."""

    # Grid layout options
    COLUMN_CHOICES = [
        ('auto', 'Auto (Responsive)'),
        ('2', '2 Columns'),
        ('3', '3 Columns'),
        ('4', '4 Columns'),
        ('6', '6 Columns'),
    ]

    CARD_STYLE_CHOICES = [
        ('standard', 'Standard'),
        ('minimal', 'Minimal'),
        ('bordered', 'Bordered'),
    ]

    columns_layout = forms.ChoiceField(
        choices=COLUMN_CHOICES,
        initial='auto',
        required=False,
        label='Grid Columns',
        help_text='Number of columns for desktop display',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    show_bios = forms.BooleanField(
        required=False,
        initial=True,
        label='Show Biographies',
        help_text='Display biography text for team members',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    card_style = forms.ChoiceField(
        choices=CARD_STYLE_CHOICES,
        initial='standard',
        required=False,
        label='Card Style',
        help_text='Visual style for team member cards',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ui_element_type='team_grid', **kwargs)

        # Add Bootstrap classes to base fields
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['label'].widget.attrs.update({'class': 'form-control'})

        # Populate options if editing
        if self.instance and self.instance.pk:
            # Store grid configuration in JSON field or as attributes
            # For now, we'll use a simple approach with custom attributes
            self.fields['columns_layout'].initial = getattr(self.instance, '_columns_layout', 'auto')
            self.fields['show_bios'].initial = getattr(self.instance, '_show_bios', True)
            self.fields['card_style'].initial = getattr(self.instance, '_card_style', 'standard')

    def save(self, commit=True):
        """Save the Team Grid UI Element."""
        instance = super().save(commit=False)

        # Store configuration as custom attributes
        # Note: These aren't actual model fields, so we'll store them in a JSON field
        # or add them as runtime attributes that can be read by the template tag
        instance._columns_layout = self.cleaned_data.get('columns_layout', 'auto')
        instance._show_bios = self.cleaned_data.get('show_bios', True)
        instance._card_style = self.cleaned_data.get('card_style', 'standard')

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
            'Team Members Grid UI Element',
            'A grid display of team members with profile photos, names, titles/positions, and ORCID identifiers. '
            'You can add up to 50 team members with optional biographies and website links.'
        )

        # Name and Label fields
        self.add_field_row(layout, 'name', 'label', col_class='col-md-6')

        # Grid options section
        layout.append(Row(
            Column(HTML('<h5 class="mt-3 mb-3">Grid Options</h5>'), css_class='col-12'),
            css_class='row g-2'
        ))

        self.add_field_row(layout, 'columns_layout', 'card_style', col_class='col-md-4')
        self.add_field_row(layout, 'show_bios', col_class='col-md-4')

        return helper


class TeamGridCreateForm(TeamGridForm):
    """Form to create a new Team Members Grid UI Element."""

    @property
    def helper(self):
        helper = super().helper
        # Note: Items section is added in the template via formset
        helper.layout.append(get_form_buttons('Create Team Grid'))
        return helper


class TeamGridEditForm(TeamGridForm):
    """Form to edit an existing Team Members Grid UI Element."""

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
        helper.layout.append(get_form_buttons('Save Team Grid'))
        return helper
