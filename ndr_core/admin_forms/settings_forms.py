"""Forms used in the NDRCore admin interface for in-app settings."""
import json

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, HTML, ButtonHolder, Submit
from django import forms
from django.forms.widgets import Select, SelectMultiple

from ndr_core.admin_forms.admin_forms import get_form_buttons, get_info_box
from ndr_core.models import NdrCoreValue, NdrCoreImage, get_available_languages


class ImagePickerWidget(Select):
    """Widget that displays images using the image-picker plugin."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'image-picker show_html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            try:
                # Extract the actual value from ModelChoiceIteratorValue if needed
                actual_value = value.value if hasattr(value, 'value') else value

                # Skip if it's not a valid ID
                if actual_value and actual_value != '':
                    image = NdrCoreImage.objects.get(pk=actual_value)
                    option['attrs']['data-img-src'] = image.image.url
                    option['attrs']['data-img-label'] = image.alt_text or 'Image'
            except (NdrCoreImage.DoesNotExist, ValueError, TypeError):
                pass
        return option


class ImagePickerMultipleWidget(SelectMultiple):
    """Widget that displays multiple images using the image-picker plugin."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'image-picker show_html'
        self.attrs['multiple'] = 'multiple'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            try:
                # Extract the actual value from ModelChoiceIteratorValue if needed
                actual_value = value.value if hasattr(value, 'value') else value

                # Skip if it's not a valid ID
                if actual_value and actual_value != '':
                    image = NdrCoreImage.objects.get(pk=actual_value)
                    option['attrs']['data-img-src'] = image.image.url
                    option['attrs']['data-img-label'] = image.alt_text or 'Image'
            except (NdrCoreImage.DoesNotExist, ValueError, TypeError):
                pass
        return option


class SettingsListForm(forms.Form):
    """Shows a defined list of settings to change. """

    settings_list = []
    is_custom_form = False

    def __init__(self, *args, **kwargs):
        if 'settings' in kwargs:
            self.settings_list = kwargs.pop('settings')
        if 'is_custom_form' in kwargs:
            self.is_custom_form = kwargs.pop('is_custom_form')

        super().__init__(*args, **kwargs)

        initial_values = {}
        for setting in self.settings_list:
            setting_obj = NdrCoreValue.get_or_initialize(setting)
            label = setting_obj.value_label
            if self.is_custom_form:
                label = f"{setting_obj.value_name}: {setting_obj.value_label}"

            if setting_obj.value_type == NdrCoreValue.ValueType.STRING:
                self.fields[f"save_{setting}"] = forms.CharField(label=label,
                                                                 required=False,
                                                                 max_length=100,
                                                                 help_text=setting_obj.value_help_text)
            elif setting_obj.value_type == NdrCoreValue.ValueType.INTEGER:
                self.fields[f"save_{setting}"] = forms.IntegerField(label=label,
                                                                    required=False,
                                                                    help_text=setting_obj.value_help_text)
            elif setting_obj.value_type == NdrCoreValue.ValueType.BOOLEAN:
                self.fields[f"save_{setting}"] = forms.BooleanField(label=label,
                                                                    required=False,
                                                                    help_text=setting_obj.value_help_text)
            elif setting_obj.value_type == NdrCoreValue.ValueType.LIST:
                self.fields[f"save_{setting}"] = forms.ChoiceField(label=label,
                                                                   required=False,
                                                                   choices=setting_obj.get_options(),
                                                                   help_text=setting_obj.value_help_text)
            elif setting_obj.value_type == NdrCoreValue.ValueType.MULTI_LIST:
                self.fields[f"save_{setting}"] = forms.MultipleChoiceField(label=label,
                                                                           required=False,
                                                                           choices=setting_obj.get_options(),
                                                                           help_text=setting_obj.value_help_text)
            elif setting_obj.value_type == NdrCoreValue.ValueType.URL:
                self.fields[f"save_{setting}"] = forms.URLField(label=label,
                                                                required=False,
                                                                help_text=setting_obj.value_help_text)

            initial_values[f"save_{setting}"] = setting_obj.get_value()

        self.initial = initial_values

    def save_list(self):
        """Saves the settings from the form data to the database."""
        for setting in self.settings_list:
            if f"save_{setting}" in self.data:
                obj = NdrCoreValue.objects.get(value_name=setting)
                if obj.value_type == NdrCoreValue.ValueType.MULTI_LIST:
                    obj.value_value = ','.join(self.data.getlist(f"save_{setting}"))
                else:
                    obj.value_value = self.data[f"save_{setting}"]
                obj.save()
            else:
                # If the setting is not in the data and its type is BOOLEAN, it means it was unchecked.
                try:
                    obj = NdrCoreValue.objects.get(value_name=setting)
                    if obj.value_type == NdrCoreValue.ValueType.BOOLEAN:
                        obj.value_value = False
                        obj.save()
                except NdrCoreValue.DoesNotExist:
                    pass

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for setting in self.settings_list:
            cols = '12'
            if self.is_custom_form:
                cols = '11'

            form_row = Row(css_class='row g-2')
            form_row.append(Column(f"save_{setting}", css_class=f'form-group col-md-{cols} mb-0'))

            if self.is_custom_form:
                html = f'''
                <p>
                    <a href="{{% url \'ndr_core:edit_setting\' \'{setting}\' %}}" class="btn btn-sm btn-secondary">
                        <i class="fa-regular fa-pen-to-square"></i>
                    </a>
                    <a href="{{% url \'ndr_core:delete_setting\' \'{setting}\'%}}" class="btn btn-sm btn-danger">
                        <i class="fa-regular fa-delete-left"></i>
                    </a>
                </p>
                '''
                col = Column(Div(
                    HTML(html),
                    css_class="form-group"
                ), css_class='form-group col-md-1 mb-0')
                form_row.append(col)
            layout.append(form_row)

        layout.append(get_form_buttons('Save Settings'))
        return helper


class SettingForm(forms.ModelForm):
    """Base form to create or edit a custom Setting. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreValue
        fields = ['value_name', 'value_label', 'value_help_text', 'value_value']

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        layout = helper.layout = Layout()
        helper.form_method = "POST"

        form_row = Row(
            Column('value_name', css_class='form-group col-md-6 mb-0'),
            Column('value_label', css_class='form-group col-md-6 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('value_help_text', css_class='form-group col-md-12 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('value_value', css_class='form-group col-md-6 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)
        return helper


class SettingCreateForm(SettingForm):
    """Form to create a custom setting. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Create New User Setting'))
        return helper


class SettingEditForm(SettingForm):
    """Form to edit a custom setting. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save User Setting'))
        return helper


class SettingsImportForm(forms.Form):
    """Form to import settings from a json file. """

    settings_file = forms.FileField(help_text='Select your exported settings file. '
                                              'Existing settings with identical names are updated.')

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        helper.layout = Layout()

        form_row = Row(
            Column('settings_file', css_class='form-group col-md-12 mb-0'),
            css_class='row g-2'
        )
        helper.layout.append(form_row)

        helper.layout.append(get_form_buttons('Import Settings'))
        return helper


class SettingsSetReadonlyForm(forms.Form):
    """Form to set the page read only."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        helper.layout = Layout()

        bh = ButtonHolder(
            Submit("submit", "Set Page Read Only", css_class="btn-default"), css_class="modal-footer"
        )
        helper.layout.append(bh)
        return helper


class SettingsSetEditableForm(forms.Form):
    """Form to set the page editable."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        helper.layout = Layout()
        bh = ButtonHolder(
            Submit("submit", "Set Page Editable", css_class="btn-default"),
            css_class="modal-footer",
        )
        helper.layout.append(bh)
        return helper


class SettingsSetUnderConstructionForm(forms.Form):
    """Form to set the page under construction."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        helper.layout = Layout()

        bh = ButtonHolder(
            Submit("submit", "Set Page Under Construction", css_class="btn-default"),
            css_class="modal-footer",
        )
        helper.layout.append(bh)
        return helper


class SettingsSetLiveForm(forms.Form):
    """Form to set the page live."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        helper.layout = Layout()

        bh = ButtonHolder(
            Submit("submit", "Set Page Live", css_class="btn-default"),
            css_class="modal-footer",
        )
        helper.layout.append(bh)
        return helper


class LogoManagementForm(forms.Form):
    """Form to manage page logos (per language) and footer partner logos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get all available images for selection
        image_choices = [('', '-- No Logo --')]
        for img in NdrCoreImage.objects.filter(image_active=True).order_by('-uploaded_at'):
            image_choices.append((str(img.pk), img.alt_text or 'Image'))

        # Get current logo settings
        page_logos_setting = NdrCoreValue.get_or_initialize('page_logo_images')
        try:
            page_logos_data = json.loads(page_logos_setting.value_value) if page_logos_setting.value_value else {}
        except (json.JSONDecodeError, ValueError):
            page_logos_data = {}

        partner_logos_setting = NdrCoreValue.get_or_initialize('footer_partner_logo_images')
        partner_logos_data = [x.strip() for x in partner_logos_setting.value_value.split(',') if x.strip()]

        # Get base language
        base_lang_setting = NdrCoreValue.get_or_initialize('ndr_language')
        base_language = base_lang_setting.get_value()

        # Create field for base language
        self.fields[f'logo_{base_language}'] = forms.ChoiceField(
            label=f'Logo for {base_language.upper()}',
            choices=image_choices,
            required=False,
            initial=page_logos_data.get(base_language, ''),
            widget=ImagePickerWidget()
        )

        # Create fields for additional languages
        available_languages = get_available_languages()
        for lang_code, lang_name in available_languages:
            if lang_code != base_language:
                self.fields[f'logo_{lang_code}'] = forms.ChoiceField(
                    label=f'Logo for {lang_name}',
                    choices=image_choices,
                    required=False,
                    initial=page_logos_data.get(lang_code, ''),
                    widget=ImagePickerWidget()
                )

        # Create field for partner logos (multiple selection)
        self.fields['partner_logos'] = forms.MultipleChoiceField(
            label='Footer Partner Logos',
            choices=image_choices[1:],  # Exclude the "No Logo" option
            required=False,
            initial=partner_logos_data,
            help_text='Select multiple logos',
            widget=ImagePickerMultipleWidget()
        )

    def save(self):
        """Save the logo settings to the database."""
        # Save page logos
        page_logos_data = {}
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('logo_'):
                lang_code = field_name[5:]  # Remove 'logo_' prefix
                if value:  # Only save if a logo is selected
                    page_logos_data[lang_code] = int(value)

        page_logos_setting = NdrCoreValue.get_or_initialize('page_logo_images')
        page_logos_setting.value_value = json.dumps(page_logos_data)
        page_logos_setting.save()

        # Save partner logos
        partner_logos = self.cleaned_data.get('partner_logos', [])
        partner_logos_setting = NdrCoreValue.get_or_initialize('footer_partner_logo_images')
        partner_logos_setting.value_value = ','.join(partner_logos)
        partner_logos_setting.save()

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        # Info box
        layout.append(Row(
            Column(get_info_box(
                "Configure logos for your site. Page logos can be set per language for internationalization. "
                "Partner logos appear in the footer."
            ), css_class='form-group col-12'),
            css_class='row g-2'
        ))

        # Page logos section
        layout.append(Row(
            Column(HTML('<h5 class="mt-3 mb-3">Page Logos (Per Language)</h5>'), css_class='col-12'),
            css_class='row g-2'
        ))

        # Add fields for each language
        base_lang_setting = NdrCoreValue.get_or_initialize('ndr_language')
        base_language = base_lang_setting.get_value()

        layout.append(Row(
            Column(f'logo_{base_language}', css_class='form-group col-md-6'),
            css_class='row g-2'
        ))

        available_languages = get_available_languages()
        for lang_code, lang_name in available_languages:
            if lang_code != base_language:
                layout.append(Row(
                    Column(f'logo_{lang_code}', css_class='form-group col-md-6'),
                    css_class='row g-2'
                ))

        # Partner logos section
        layout.append(Row(
            Column(HTML('<h5 class="mt-4 mb-3">Footer Partner Logos</h5>'), css_class='col-12'),
            css_class='row g-2'
        ))

        layout.append(Row(
            Column('partner_logos', css_class='form-group col-md-12'),
            css_class='row g-2'
        ))

        layout.append(get_form_buttons('Save Logo Settings'))
        return helper
