"""Module for all the custom form fields. """
from django import forms
from django.utils.translation import gettext_lazy as _


class NumberRangeField(forms.CharField):
    """Field to validate a range of numbers. """

    lowest_number = 1
    highest_number = 999999

    def __init__(self, *args, **kwargs):
        if 'lowest_number' in kwargs:
            self.lowest_number = kwargs.pop('lowest_number')
        if 'highest_number' in kwargs:
            self.highest_number = kwargs.pop('highest_number')
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        """Normalize data to a list of strings."""
        # Return an empty list if no input was given.
        if not value:
            return []

        try:
            result = set()
            for part in value.split(','):
                x = part.split('-')
                result.update(range(int(x[0]), int(x[-1]) + 1))
            return sorted(result)
        except ValueError:
            raise forms.ValidationError(_('Invalid value: Format is "1,2,3-5,7"'))

    def validate(self, value):
        """Check if value consists only of valid emails."""
        # Use the parent's handling of required fields, etc.
        super().validate(value)
        if len(value) == 0:
            return
        if len(value) == 1:
            if value[0] < self.lowest_number or value[0] > self.highest_number:
                raise forms.ValidationError(
                    _('Value is out of range. ({}-{})'  # pylint: disable=consider-using-f-string
                      .format(self.lowest_number,
                              self.highest_number)))
        if len(value) > 1:
            if value[0] < self.lowest_number or value[-1] > self.highest_number:
                raise forms.ValidationError(
                    _('Value is out of range. ({}-{})'  # pylint: disable=consider-using-f-string
                      .format(self.lowest_number,
                              self.highest_number)))

        if value is None:
            raise forms.ValidationError(_('Invalid value'))
