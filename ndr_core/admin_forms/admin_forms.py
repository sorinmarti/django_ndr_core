"""Contains general forms used in the NDRCore admin interface."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, ButtonHolder, HTML
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.forms import forms


class NdrCoreLoginForm(AuthenticationForm):
    """Takes Django's login form and adds a button to it,
    so it can be rendered with crispy forms """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('login', 'Login'))


class NdrCoreChangePasswordForm(PasswordChangeForm):
    """Takes Django's change password form and adds an input to it,
    so it can be rendered with crispy forms """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('login', 'Change Password'))


class ConnectWithNdrCoreForm(forms.Form):
    """A Form to activate or deactivate the connection with the NDRCore.org website. """

    def __init__(self, *args, **kwargs):
        """Initialises all needed form fields."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('submit', 'Connect with NDRCore.org'))


class UploadGoogleVerificationFileForm(forms.Form):
    """A Form to upload a Google Search Console verification file. """

    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        """Initialises all needed form fields."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('submit', 'Upload'))


def get_form_buttons(submit_text):
    """Returns a button holder with a submit button with the given text.
    This is a convenience function for all forms that are used in the
    NDRCore admin interface. """
    bh = ButtonHolder(
            Submit('submit', submit_text, css_class='btn-default'),
            css_class="modal-footer"
        )
    return bh


def get_info_box(text, item_id="id_info_box", box_id="info_box"):
    """Returns an info box with the given text.
    This is a convenience function for all forms that are used in the
    NDRCore admin interface. """
    alert_html = f'<div class="alert alert-info small m-3" role="alert" id="{box_id}">' \
                 f'  <i class="fa-regular fa-circle-info"></i>' \
                 f'  <span id="{item_id}">' \
                 f'    {text}' \
                 f'  </span>' \
                 f'</div>'
    return HTML(alert_html)
