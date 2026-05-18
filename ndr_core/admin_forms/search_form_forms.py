"""Form to create or edit a search configuration search form. """
from django import forms


class SearchConfigurationFormEditForm(forms.Form):
    """Minimal form — the visual grid editor in the template owns the layout.
    The hidden field carries the serialised JSON produced by grid_editor.js."""

    grid_config = forms.CharField(widget=forms.HiddenInput(), required=False)