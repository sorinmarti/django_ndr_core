"""Contains general forms used in the NDRCore admin interface."""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, ButtonHolder
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm


class NdrCoreLoginForm(AuthenticationForm):
    """Takes Django's login form and adds a button to it, so it can be rendered with crispy forms """

    def __init__(self, *args, **kwargs):
        super(NdrCoreLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('login', 'Login'))


class NdrCoreChangePasswordForm(PasswordChangeForm):
    """Takes Django's change password form and adds an input to it, so it can be rendered with crispy forms """

    def __init__(self, *args, **kwargs):
        super(NdrCoreChangePasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('login', 'Change Password'))


def get_form_buttons(submit_text):
    """Returns a button holder with a submit button with the given text. This is a convenience function for all
    forms that are used in the NDRCore admin interface. """
    bh = ButtonHolder(
            Submit('submit', submit_text, css_class='btn-default'),
            css_class="modal-footer"
        )
    return bh

