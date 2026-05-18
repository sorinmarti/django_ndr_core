"""Forms for the result card configuration. """
from django import forms


class SearchConfigurationResultEditForm(forms.Form):
    """Minimal form — the visual grid editors in the template own the layout.
    The hidden fields carry serialised JSON produced by grid_editor.js."""

    grid_config_normal  = forms.CharField(widget=forms.HiddenInput(), required=False)
    grid_config_compact = forms.CharField(widget=forms.HiddenInput(), required=False)