"""Contains forms used in the NDRCore admin interface for the creation or edit of NDR pages."""
from django_ckeditor_5.widgets import CKEditor5Widget
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms
from django.urls import reverse
from django_select2 import forms as s2forms

from ndr_core.admin_forms.settings_forms import SettingsListForm
from ndr_core.admin_forms.admin_forms import get_form_buttons, get_info_box
from ndr_core.admin_forms.ui_element_types.base_forms import ImageChoiceField
from ndr_core.models import (
    NdrCoreSearchConfiguration,
    NdrCorePage,
    NdrCoreValue,
    NdrCoreRichTextTranslation,
    NdrCoreImage
)


class SearchConfigurationWidget(s2forms.ModelSelect2MultipleWidget):     # pylint: disable=too-many-ancestors
    """Widget to display a multi select2 dropdown for search configurations. """

    model = NdrCoreSearchConfiguration
    search_fields = [
        'conf_name__icontains'
    ]


class PageForm(forms.ModelForm):
    """Base form to create or edit an NDRCore page. The form contains fields for search
    configurations etc. which are only needed for certain page types. Unused fields are
    hidden via JS in the template the form is used."""

    search_configs = forms.ModelMultipleChoiceField(
        queryset=NdrCoreSearchConfiguration.objects.filter().order_by('conf_name'),
        required=False,
        widget=SearchConfigurationWidget(
            attrs={'data-minimum-input-length': 0}))

    parent_page = forms.ModelChoiceField(queryset=NdrCorePage.objects.filter(parent_page=None),
                                         required=False,
                                         help_text="If you want this page to be a sub-page of another "
                                                   "one, you can choose the parent page here")

    # Background image field with image picker
    background_image = ImageChoiceField(
        queryset=NdrCoreImage.objects.filter(image_active=True).order_by('-uploaded_at'),
        required=False,
        label='Background Image (Light Mode)',
        help_text='Select a background image for this page'
    )

    background_image_dark = ImageChoiceField(
        queryset=NdrCoreImage.objects.filter(image_active=True).order_by('-uploaded_at'),
        required=False,
        label='Background Image (Dark Mode)',
        help_text='Optional: Select a different background image for dark mode (falls back to light mode image if not set)'
    )

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCorePage
        fields = ['name', 'show_page_title', 'label', 'show_in_navigation', 'show_navigation', 'show_footer',
                  'center_content', 'page_type', 'parent_page', 'search_configs', 'view_name', 'template_text',
                  'use_default_background', 'background_image', 'background_image_dark', 'background_display_mode',
                  'background_position', 'background_size', 'overlay_enabled', 'overlay_color', 'overlay_opacity']

    def __init__(self, *args, **kwargs):
        """Init class and create form helper."""
        super().__init__(*args, **kwargs)

        self.main_language = NdrCoreValue.objects.get(value_name='ndr_language').get_value()
        self.additional_languages = NdrCoreValue.objects.get(value_name='available_languages').get_value()

        for lang in self.additional_languages:
            self.fields[f'template_text_{lang}'] = forms.CharField(label=f"Template Text ({lang})",
                                                                   required=False,
                                                                   widget=CKEditor5Widget(config_name='page_editor'))
            try:
                translation = NdrCoreRichTextTranslation.objects.get(language=lang,
                                                                     table_name='NdrCorePage',
                                                                     object_id=self.instance.pk,
                                                                     field_name='template_text')
                self.initial[f'template_text_{lang}'] = translation.translation
            except NdrCoreRichTextTranslation.DoesNotExist:
                pass

    def clean(self):
        """clean() is executed when the form is sent to check it. Here, page types are checked against its
        requirements. Example: A simple search needs an API config but no List- and SearchConfiguration."""
        cleaned_data = super().clean()
        page_type = cleaned_data['page_type']
        search_configs = cleaned_data['search_configs']

        if page_type == NdrCorePage.PageType.TEMPLATE:
            # no additional fields required
            pass
        elif page_type == NdrCorePage.PageType.SEARCH:
            if search_configs.count() == 0:
                msg = "You must provide at least one Search configuration for Search pages."
                self.add_error('search_configs', msg)
        elif page_type == NdrCorePage.PageType.DATA_LIST:
            if search_configs.count() == 0:
                msg = "You must provide exactly one Search configuration for Data List pages."
                self.add_error('search_configs', msg)
            elif search_configs.count() > 1:
                msg = "You can only provide one Search configuration for Data List pages."
                self.add_error('search_configs', msg)
        elif page_type == NdrCorePage.PageType.CONTACT:
            if NdrCorePage.objects.filter(page_type=NdrCorePage.PageType.CONTACT).count() > 0:
                if self.instance.pk is None:
                    msg = "You can't have more than one contact page."
                    self.add_error('page_type', msg)
        else:
            pass

    def save_translations(self):
        """Saves the translations for the page."""
        for lang in self.additional_languages:
            if f'template_text_{lang}' in self.cleaned_data:
                trans = NdrCoreRichTextTranslation.objects.get_or_create(language=lang,
                                                                         table_name='NdrCorePage',
                                                                         object_id=self.instance.pk,
                                                                         field_name='template_text')
                trans[0].translation = self.cleaned_data[f'template_text_{lang}']
                trans[0].save()

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('name', css_class='form-group col-md-6 mb-0'),
            Column('label', css_class='form-group col-md-6 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column("show_page_title", css_class="form-group col-md-6 mb-0"),
            Column("show_in_navigation", css_class="form-group col-md-6 mb-0"),
            css_class="form-row",
        )
        layout.append(form_row)

        form_row = Row(
            Column("show_navigation", css_class="form-group col-md-4 mb-0"),
            Column("show_footer", css_class="form-group col-md-4 mb-0"),
            Column("center_content", css_class="form-group col-md-4 mb-0"),
            css_class="form-row",
        )
        layout.append(form_row)

        form_row = Row(
            Column('view_name', css_class='form-group col-md-6 mb-0'),
            Column('parent_page', css_class='form-group col-md-6 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('page_type', css_class='form-group col-md-6 mb-0'),
            Column(
                get_info_box('', 'page_type_info'),
                css_class='form-group col-md-6 mb-0'
            ),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('search_configs', css_class='form-group col-md-12 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        # Background Image Settings Tab
        background_tab_content = [
            Row(
                Column('use_default_background', css_class='form-group col-md-12 mb-0'),
                css_class='row g-2'
            ),
            Row(
                Column('background_image', css_class='form-group col-md-6 mb-0'),
                Column('background_image_dark', css_class='form-group col-md-6 mb-0'),
                css_class='row g-2'
            ),
            Row(
                Column('background_display_mode', css_class='form-group col-md-6 mb-0'),
                Column('background_position', css_class='form-group col-md-3 mb-0'),
                Column('background_size', css_class='form-group col-md-3 mb-0'),
                css_class='row g-2'
            ),
            Row(
                Column(
                    HTML('<h5 class="mt-3 mb-2">Overlay Settings (for better text readability)</h5>'),
                    css_class='col-md-12'
                ),
                css_class='row g-2'
            ),
            Row(
                Column('overlay_enabled', css_class='form-group col-md-4 mb-0'),
                Column('overlay_color', css_class='form-group col-md-4 mb-0'),
                Column('overlay_opacity', css_class='form-group col-md-4 mb-0'),
                css_class='row g-2'
            ),
        ]

        if len(self.additional_languages) > 0:
            # Tabs for content and background
            tab_holder = TabHolder(
                Tab('Content (' + self.main_language + ')', 'template_text')
            )
            for lang in self.additional_languages:
                tab_holder.append(Tab('Content (' + lang + ')', f'template_text_{lang}'))

            # Add Background tab with all background settings
            tab_holder.append(Tab('Background Image', *background_tab_content))

            form_row = Row(
                Column(tab_holder, css_class='form-group center col-md-12 mb-0'),
                css_class='row g-2'
            )
            layout.append(form_row)
        else:
            # Tabs for content and background (no multiple languages)
            tab_holder = TabHolder(
                Tab('Content', 'template_text'),
                Tab('Background Image', *background_tab_content)
            )
            form_row = Row(
                Column(tab_holder, css_class='form-group center col-md-12 mb-0'),
                css_class='row g-2'
            )
            layout.append(form_row)

        return helper


class PageCreateForm(PageForm):
    """Form to create a page. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Create New Page'))
        return helper


class PageEditForm(PageForm):
    """Form to edit a page. Extends the base form class and adds an 'edit' button."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.initial["view_name"] == "index":
            self.fields['view_name'].disabled = True
            self.fields['view_name'].help_text = "This is your landing page you can\'t change its view name."

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save Page', include_save_and_continue=True))
        return helper


class FooterForm(SettingsListForm):
    """Form to edit the footer settings."""

    def __init__(self, *args, **kwargs):
        kwargs['settings'] = ["footer_show_partners", "footer_show_main_navigation", "footer_show_socials",
                              "footer_copyright_text"]
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = super().helper
        layout = helper.layout = Layout()

        form_row = Row(
            Column('save_footer_show_partners', css_class='form-group col-md-10 mb-0'),
            Column(HTML(f'<a href="{reverse("ndr_core:view_images", kwargs={"group": "logos"})}" '
                        f'class="btn btn-sm btn-secondary">Manage Partner Logos</a>'),
                   css_class='form-group col-md-2 mb-0 text-right'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('save_footer_show_main_navigation', css_class='form-group col-md-12 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)

        html = f'''
        <a href="{reverse("ndr_core:view_settings", kwargs={"group": "socials"})}" 
        class="btn btn-sm btn-secondary">Manage Social Links</a>
        '''
        form_row = Row(
            Column('save_footer_show_socials', css_class='form-group col-md-10 mb-0'),
            Column(HTML(html),
                   css_class='form-group col-md-2 mb-0 text-right'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('save_footer_copyright_text', css_class='form-group col-md-12 mb-0'),
            css_class='row g-2'
        )
        layout.append(form_row)
        layout.append(get_form_buttons('Save Settings'))
        return helper


class NotFoundForm(forms.Form):
    """Form to edit the 404 page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        layout = helper.layout = Layout()
        layout.append(get_form_buttons('Save Settings'))
        return helper
