"""Forms for Zotero Group Library UI Element type."""
import re

from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms
from django.core.cache import cache

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUIElement, NdrCoreUiElementItem
from .base_forms import BaseUIElementForm


def _zotero_cache_key(group_id, api_key=''):
    import hashlib
    key_hash = hashlib.md5(api_key.encode()).hexdigest()[:8] if api_key else 'pub'
    safe_id = re.sub(r'[^a-zA-Z0-9]', '_', group_id)
    return f'ndr_zotero_{safe_id}_{key_hash}'


class ZoteroGroupForm(BaseUIElementForm):
    """Form for Zotero Group Library UI Element."""

    group_id = forms.CharField(
        required=True,
        label='Zotero Group ID',
        help_text='The numeric ID of the Zotero group library '
                  '(found in the URL at zotero.org/groups/&lt;ID&gt;).'
    )

    api_key = forms.CharField(
        required=False,
        label='API Key',
        help_text='Optional API key for private libraries. Leave blank for public groups.',
        widget=forms.PasswordInput(render_value=True)
    )

    section_title = forms.CharField(
        required=False,
        label='Section Title',
        help_text='Optional heading displayed above the bibliography list.'
    )

    items_per_page = forms.IntegerField(
        required=False,
        initial=20,
        min_value=1,
        max_value=100,
        label='Items Per Page',
        help_text='Number of publications shown per page (1–100, default 20).'
    )

    cache_ttl_hours = forms.IntegerField(
        required=False,
        initial=24,
        min_value=1,
        max_value=168,
        label='Cache Duration (hours)',
        help_text='How long to keep a local copy before re-fetching from Zotero (1–168 h, default 24).'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ui_element_type='zotero_group', **kwargs)

    def save(self, commit=True):
        """Save the Zotero Group UI Element and its single item."""
        instance = super().save(commit=commit)
        if commit:
            # Clear stale cache for the old configuration before overwriting
            old_items = instance.ndrcoreuielementitem_set.all()
            for old_item in old_items:
                if old_item.object_id:
                    cache.delete(_zotero_cache_key(old_item.object_id, old_item.text or ''))

            instance.ndrcoreuielementitem_set.all().delete()

            group_id = self.cleaned_data.get('group_id', '')
            api_key = self.cleaned_data.get('api_key', '')
            items_per_page = self.cleaned_data.get('items_per_page') or 20
            cache_ttl_hours = self.cleaned_data.get('cache_ttl_hours') or 24

            NdrCoreUiElementItem.objects.create(
                belongs_to=instance,
                order_idx=0,
                object_id=group_id,
                text=api_key,
                title=self.cleaned_data.get('section_title', ''),
                provider=f'{items_per_page}:{cache_ttl_hours}',
            )
        return instance

    @property
    def helper(self):
        """Creates and returns the form helper."""
        helper = self.get_base_helper()
        layout = helper.layout

        self.add_info_section(
            layout,
            'Zotero Group Library',
            'Display a bibliography from a Zotero group library. '
            'Enter the group ID found in the URL at zotero.org/groups/&lt;ID&gt;/. '
            'Public libraries do not require an API key. '
            'Items are fetched once and cached locally for the configured duration.'
        )

        self.add_field_row(layout, 'name', 'label', col_class='col-md-6')

        layout.append(Row(
            Column(HTML('<h5 class="mt-3 mb-3">Zotero Configuration</h5>'), css_class='col-12'),
            css_class='row g-2'
        ))

        self.add_field_row(layout, 'group_id', 'api_key', col_class='col-md-6')
        self.add_field_row(layout, 'section_title', col_class='col-md-12')
        self.add_field_row(layout, 'items_per_page', 'cache_ttl_hours', col_class='col-md-6')

        return helper


class ZoteroGroupCreateForm(ZoteroGroupForm):
    """Form to create a new Zotero Group Library UI Element."""

    @property
    def helper(self):
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Zotero Library'))
        return helper


class ZoteroGroupEditForm(ZoteroGroupForm):
    """Form to edit an existing Zotero Group Library UI Element."""

    def __init__(self, *args, **kwargs):
        self._original_name = kwargs['instance'].name if 'instance' in kwargs else None
        super().__init__(*args, **kwargs)
        self.fields['name'].help_text = (
            'Unique slug/identifier. Can be changed — renaming will preserve all settings.'
        )

        if self.instance and self.instance.pk:
            items = self.instance.items()
            if items:
                item = items[0]
                self.fields['group_id'].initial = item.object_id
                self.fields['api_key'].initial = item.text
                self.fields['section_title'].initial = item.title
                # Parse "items_per_page:cache_ttl_hours" from provider
                provider = item.provider or ''
                if ':' in provider:
                    parts = provider.split(':', 1)
                    try:
                        self.fields['items_per_page'].initial = int(parts[0])
                    except (ValueError, TypeError):
                        self.fields['items_per_page'].initial = 20
                    try:
                        self.fields['cache_ttl_hours'].initial = int(parts[1])
                    except (ValueError, TypeError):
                        self.fields['cache_ttl_hours'].initial = 24
                else:
                    try:
                        self.fields['items_per_page'].initial = int(provider) if provider else 20
                    except (ValueError, TypeError):
                        self.fields['items_per_page'].initial = 20
                    self.fields['cache_ttl_hours'].initial = 24

    def save(self, commit=True):
        """Save with special handling for name changes (PK changes)."""
        name_changed = self._original_name and self._original_name != self.cleaned_data.get('name')

        if name_changed and commit:
            old_instance = NdrCoreUIElement.objects.get(name=self._original_name)
            new_instance = super().save(commit=True)
            old_instance.delete()
            return new_instance

        return super().save(commit=commit)

    @property
    def helper(self):
        helper = super().helper
        helper.layout.append(get_form_buttons('Save Zotero Library'))
        return helper