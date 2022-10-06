from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import AuthenticationForm

from ndr_core.models import NdrCorePage, ApiConfiguration


class PageForm(forms.ModelForm):
    class Meta:
        model = NdrCorePage
        fields = ['name', 'label', 'page_type', 'view_name']

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('submit', 'Create New Page'))


class ApiForm(forms.ModelForm):
    class Meta:
        model = ApiConfiguration
        fields = ['api_name', 'api_host', 'api_protocol', 'api_port', 'api_label', 'api_page_size']

    def __init__(self, *args, **kwargs):
        super(ApiForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('submit', 'Create Api Configuration'))


class NdrCoreLoginForm(AuthenticationForm):
    """Takes Django's login form and adds an input to it so it can be rendered with crispy forms """

    def __init__(self, *args, **kwargs):
        super(NdrCoreLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(MySubmit('login', 'Login'))