"""Contains forms used in the NDRCore admin interface for the creation or edit of color palettes."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreColorScheme


class ColorPaletteForm(forms.ModelForm):
    """Form to create or edit a palette. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreColorScheme
        fields = '__all__'

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        layout = helper.layout = Layout()
        helper.form_method = "POST"

        # Basic Information
        layout.append(HTML('<h4 class="mt-3 mb-3">Basic Information</h4>'))
        layout.append(Row(
            Column('scheme_label', css_class='form-group col-md-6 mb-0'),
            Column('scheme_name', css_class='form-group col-md-6 mb-0'),
            css_class='row g-2'
        ))

        # Typography
        layout.append(HTML('<h4 class="mt-4 mb-3">Typography</h4>'))
        layout.append(Row(
            Column('font_family', css_class='form-group col-md-12 mb-0'),
            css_class='row g-2'
        ))
        layout.append(Row(
            Column('h1_size', css_class='form-group col-md-3 mb-0'),
            Column('h2_size', css_class='form-group col-md-3 mb-0'),
            Column('h3_size', css_class='form-group col-md-3 mb-0'),
            Column('h4_size', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        # Brand Panel (for unibas_brand style)
        layout.append(HTML('<h4 class="mt-4 mb-3">Brand Panel Colors</h4>'))
        layout.append(Row(
            Column('brand_panel_bg', css_class='form-group col-md-3 mb-0'),
            Column('brand_panel_text', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        # Light Mode Colors
        layout.append(HTML('<h3 class="mt-5 mb-3 text-primary">Light Mode Colors</h3>'))

        layout.append(HTML('<h5 class="mt-3 mb-2">Backgrounds</h5>'))
        layout.append(Row(
            Column('background_color', css_class='form-group col-md-3 mb-0'),
            Column('container_bg_color', css_class='form-group col-md-3 mb-0'),
            Column('footer_bg', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Text</h5>'))
        layout.append(Row(
            Column('text_color', css_class='form-group col-md-3 mb-0'),
            Column('title_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Navigation</h5>'))
        layout.append(Row(
            Column('link_color', css_class='form-group col-md-3 mb-0'),
            Column('nav_link_color', css_class='form-group col-md-3 mb-0'),
            Column('nav_active_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Tabs</h5>'))
        layout.append(Row(
            Column('tab_title_color', css_class='form-group col-md-3 mb-0'),
            Column('tab_active_title_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Footer</h5>'))
        layout.append(Row(
            Column('footer_link_color', css_class='form-group col-md-3 mb-0'),
            Column('footer_link_hover_color', css_class='form-group col-md-3 mb-0'),
            Column('powered_by_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Accents</h5>'))
        layout.append(Row(
            Column('accent_color_1', css_class='form-group col-md-3 mb-0'),
            Column('accent_color_2', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Primary Buttons</h5>'))
        layout.append(Row(
            Column('button_color', css_class='form-group col-md-3 mb-0'),
            Column('button_hover_color', css_class='form-group col-md-3 mb-0'),
            Column('button_text_color', css_class='form-group col-md-3 mb-0'),
            Column('button_border_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Secondary Buttons</h5>'))
        layout.append(Row(
            Column('second_button_color', css_class='form-group col-md-3 mb-0'),
            Column('second_button_hover_color', css_class='form-group col-md-3 mb-0'),
            Column('second_button_text_color', css_class='form-group col-md-3 mb-0'),
            Column('second_button_border_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Form Fields</h5>'))
        layout.append(Row(
            Column('form_field_bg', css_class='form-group col-md-3 mb-0'),
            Column('form_field_fg', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Alerts</h5>'))
        layout.append(Row(
            Column('info_color', css_class='form-group col-md-3 mb-0'),
            Column('success_color', css_class='form-group col-md-3 mb-0'),
            Column('error_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        # Dark Mode Colors
        layout.append(HTML('<h3 class="mt-5 mb-3 text-secondary">Dark Mode Colors</h3>'))

        layout.append(HTML('<h5 class="mt-3 mb-2">Brand Panel (Dark)</h5>'))
        layout.append(Row(
            Column('dark_brand_panel_bg', css_class='form-group col-md-3 mb-0'),
            Column('dark_brand_panel_text', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Backgrounds (Dark)</h5>'))
        layout.append(Row(
            Column('dark_background_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_container_bg_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_footer_bg', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Text (Dark)</h5>'))
        layout.append(Row(
            Column('dark_text_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_title_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Navigation (Dark)</h5>'))
        layout.append(Row(
            Column('dark_link_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_nav_link_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_nav_active_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Tabs (Dark)</h5>'))
        layout.append(Row(
            Column('dark_tab_title_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_tab_active_title_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Footer (Dark)</h5>'))
        layout.append(Row(
            Column('dark_footer_link_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_footer_link_hover_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_powered_by_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Accents (Dark)</h5>'))
        layout.append(Row(
            Column('dark_accent_color_1', css_class='form-group col-md-3 mb-0'),
            Column('dark_accent_color_2', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Primary Buttons (Dark)</h5>'))
        layout.append(Row(
            Column('dark_button_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_button_hover_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_button_text_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_button_border_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Secondary Buttons (Dark)</h5>'))
        layout.append(Row(
            Column('dark_second_button_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_second_button_hover_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_second_button_text_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_second_button_border_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Form Fields (Dark)</h5>'))
        layout.append(Row(
            Column('dark_form_field_bg', css_class='form-group col-md-3 mb-0'),
            Column('dark_form_field_fg', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        layout.append(HTML('<h5 class="mt-3 mb-2">Alerts (Dark)</h5>'))
        layout.append(Row(
            Column('dark_info_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_success_color', css_class='form-group col-md-3 mb-0'),
            Column('dark_error_color', css_class='form-group col-md-3 mb-0'),
            css_class='row g-2'
        ))

        return helper


class ColorPaletteCreateForm(ColorPaletteForm):
    """Form to create a color palette from. """

    @property
    def helper(self):
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Color Palette'))
        return helper


class ColorPaletteEditForm(ColorPaletteForm):
    """Form to edit a color palette. """

    @property
    def helper(self):
        helper = super().helper
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
            css_class='row g-2'
        )
        helper.layout.append(form_row)

        helper.layout.append(get_form_buttons('Import Color Palette'))
        return helper
