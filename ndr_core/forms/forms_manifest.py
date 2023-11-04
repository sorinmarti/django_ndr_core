from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django.utils.translation import gettext_lazy as _
from django import forms
from ndr_core.forms.forms_base import _NdrCoreForm
from ndr_core.models import NdrCoreManifest
from django_select2 import forms as s2forms

class ManifestSelectionForm(_NdrCoreForm):
    """Form class for the manifest selection. Provides a dropdown to select a manifest and a button to show it. """

    def __init__(self, *args, **kwargs):
        """Initialises the form fields. """
        super().__init__(*args, **kwargs)

        self.fields['manifest'] = forms.ModelChoiceField(label=_('Manifest'),
                                                         queryset=NdrCoreManifest.objects.all(),
                                                         required=True,
                                                         help_text=_('Choose the manifest to display.'),
                                                         widget=s2forms.Select2Widget())

    @property
    def helper(self):
        """Sets the layout of the form fields. """

        helper = FormHelper()
        helper.form_method = "GET"
        helper.form_show_labels = False
        layout = helper.layout = Layout()

        from ndr_core.forms.widgets import NdrCoreFormSubmit
        form_row = Row(
            Column('manifest', css_class='form-group col-md-9 mb-0'),
            Column(NdrCoreFormSubmit('submit', _('Show')), css_class='form-group col-md-3 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        return helper