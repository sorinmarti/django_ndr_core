from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from ndr_core.models import NdrCorePage


class PageForm(forms.ModelForm):
    class Meta:
        model = NdrCorePage
        fields = ['name', 'label', 'page_type', 'view_name']

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('submit', 'Create New Page'))
