"""Forms for the contact form."""
from django_recaptcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Row, Column, Layout
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from ndr_core.forms.forms_base import _NdrCoreForm
from ndr_core.models import NdrCoreValue, NdrCoreUserMessage


class ContactForm(ModelForm, _NdrCoreForm): # pylint: disable=too-many-ancestors
    """Provides a form to send a message to the site admin. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreUserMessage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['message_subject'].initial = NdrCoreValue.get_or_initialize(
            value_name='contact_form_default_subject').translated_value()
        self.fields['message_subject'].label = _('Message Subject')
        self.fields['message_ret_email'].label = _('Your E-Mail address')
        self.fields['message_text'].label = _('Message Text')

        if NdrCoreValue.get_or_initialize(value_name='contact_form_display_captcha').get_value():
            self.fields['captcha'] = ReCaptchaField()

    @property
    def helper(self):
        """Creates and returns the form layout."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('message_subject', css_class='form-group col-md-6 mb-0'),
            Column('message_ret_email', css_class='form-group col-md-6 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('message_text', css_class='form-group col-md-12 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        if NdrCoreValue.get_or_initialize(value_name='contact_form_display_captcha').get_value():
            form_row = Row(
                Column('captcha', css_class='form-group col-md-12 mb-0'),
                css_class='row g-2'
            )
            layout.append(form_row)

        layout.append(_NdrCoreForm.get_button_line('submit', _('Send Message')))

        return helper
