"""Contains general forms used in the NDRCore admin interface."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button, ButtonHolder
from django.contrib.auth.forms import AuthenticationForm


class NdrCoreLoginForm(AuthenticationForm):
    """Takes Django's login form and adds an input to it so it can be rendered with crispy forms """

    def __init__(self, *args, **kwargs):
        super(NdrCoreLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('login', 'Login'))


def get_form_buttons(submit_text):
    bh = ButtonHolder(
            Button('cancel', 'Cancel', css_class="btn btn-md btn-default",
                   data_dismiss="modal"),
            Submit('submit', submit_text, css_class='btn-default'),
            css_class="modal-footer"
        )
    return bh