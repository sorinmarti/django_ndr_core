"""Base module for all NDR Core forms.  """
from crispy_forms.layout import Div
from django import forms

from ndr_core.forms.widgets import NdrCoreFormSubmit


class _NdrCoreForm(forms.Form):
    """Base form class for all (non-admin) NDR Core forms."""

    ndr_page = None

    def __init__(self, *args, **kwargs):
        """Init the form class. Save the ndr page if it is provided."""
        if "ndr_page" in kwargs:
            self.ndr_page = kwargs.pop("ndr_page")
        if "instance" in kwargs:
            kwargs.pop("instance")
        if "search_config" in kwargs:
            kwargs.pop("search_config")

        super(forms.Form, self).__init__(*args, **kwargs)

    @staticmethod
    def query_dict_to_dict(query_dict):
        """Translates query dict of form return to default dict and removes single value lists."""
        data = {}
        for key in query_dict.keys():
            v = query_dict.getlist(key)
            if len(v) == 1:
                v = v[0]
            data[key] = v
        return data

    @staticmethod
    def get_button_line(button_name, button_label):
        """Create and return right aligned search button."""

        div = Div(
            Div(css_class="col-md-8"),
            Div(
                Div(
                    NdrCoreFormSubmit(button_name, button_label), css_class="text-right"
                ),
                css_class="col-md-4",
            ),
            css_class="form-row",
        )
        return div
