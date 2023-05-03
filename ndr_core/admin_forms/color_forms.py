"""Contains forms used in the NDRCore admin interface for the creation or edit of color palettes."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreColorScheme


class ColorPaletteForm(forms.ModelForm):
    """Form to create or edit a palette. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreColorScheme
        exclude = []

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        layout = helper.layout = Layout()
        helper.form_method = "POST"

        form_row = Row(
                Column('scheme_label', css_class='form-group col-md-6 mb-0'),
                Column('scheme_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            )
        layout.append(form_row)

        form_row = Row(
            Column('background_color', css_class='form-group col-md-3 mb-0'),
            Column('container_bg_color', css_class='form-group col-md-3 mb-0'),
            Column('footer_bg', css_class='form-group col-md-3 mb-0'),

            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('text_color', css_class='form-group col-md-3 mb-0'),
            Column('title_color', css_class='form-group col-md-3 mb-0'),
            Column('link_color', css_class='form-group col-md-3 mb-0'),

            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('accent_color_1', css_class='form-group col-md-3 mb-0'),
            Column('accent_color_2', css_class='form-group col-md-3 mb-0'),

            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('button_color', css_class='form-group col-md-3 mb-0'),
            Column('button_hover_color', css_class='form-group col-md-3 mb-0'),
            Column('button_text_color', css_class='form-group col-md-3 mb-0'),
            Column('button_border_color', css_class='form-group col-md-3 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('second_button_color', css_class='form-group col-md-3 mb-0'),
            Column('second_button_hover_color', css_class='form-group col-md-3 mb-0'),
            Column('second_button_text_color', css_class='form-group col-md-3 mb-0'),
            Column('second_button_border_color', css_class='form-group col-md-3 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('form_field_bg', css_class='form-group col-md-3 mb-0'),
            Column('form_field_fg', css_class='form-group col-md-3 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('info_color', css_class='form-group col-md-3 mb-0'),
            Column('success_color', css_class='form-group col-md-3 mb-0'),
            Column('error_color', css_class='form-group col-md-3 mb-0'),

            css_class='form-row'
        )
        layout.append(form_row)

        return helper


class ColorPaletteCreateForm(ColorPaletteForm):
    """Form to create a color palette from. """

    @property
    def helper(self):
        helper = super(ColorPaletteCreateForm, self).helper
        helper.layout.append(get_form_buttons('Create Color Palette'))
        return helper


class ColorPaletteEditForm(ColorPaletteForm):
    """Form to edit a color palette. """

    @property
    def helper(self):
        helper = super(ColorPaletteEditForm, self).helper
        helper.layout.append(get_form_buttons('Save Color Palette'))
        return helper


class ColorPaletteImportForm(forms.Form):
    """Form to import a json file to create or update a color palette. """

    palette_file = forms.FileField(help_text='Select your exported scheme file. '
                                             'Existing schemes with identical names are updated.')

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        helper.layout = Layout()

        form_row = Row(
            Column('palette_file', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        helper.layout.append(form_row)

        helper.layout.append(get_form_buttons('Import Color Palette'))
        return helper
