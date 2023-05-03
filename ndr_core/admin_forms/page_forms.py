"""Contains forms used in the NDRCore admin interface for the creation or edit of NDR pages."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms
from django.urls import reverse
from django_select2 import forms as s2forms

from ndr_core.admin_forms.settings_forms import SettingsListForm
from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreSearchConfiguration, NdrCoreFilterableListConfiguration, NdrCorePage


class SearchConfigurationWidget(s2forms.ModelSelect2MultipleWidget):
    """Widget to display a multi select2 dropdown for search configurations. """

    model = NdrCoreSearchConfiguration
    search_fields = [
        'conf_name__icontains'
    ]


class FilteredListWidget(s2forms.ModelSelect2MultipleWidget):
    """Widget to display a multi select2 dropdown for list configurations. """

    model = NdrCoreFilterableListConfiguration
    search_fields = [
        'list_name__icontains'
    ]


class PageForm(forms.ModelForm):
    """Base form to create or edit an NDRCore page. The form contains fields for search configurations etc. which are only needed
    for certain page types. Unused fields are hidden via JS in the template the form is used."""

    search_configs = forms.ModelMultipleChoiceField(
        queryset=NdrCoreSearchConfiguration.objects.filter().order_by('conf_name'),
        required=False,
        widget=SearchConfigurationWidget(
            attrs={'data-minimum-input-length': 0}))

    list_configs = forms.ModelMultipleChoiceField(queryset=NdrCoreFilterableListConfiguration.objects.all(). \
                                                  order_by('list_name'),
                                                  required=False,
                                                  widget=FilteredListWidget(
                                                      attrs={'data-minimum-input-length': 0}))

    parent_page = forms.ModelChoiceField(queryset=NdrCorePage.objects.filter(parent_page=None),
                                         required=False, help_text="If you want this page to be a sub-page of another "
                                                                   "one, you can choose the parent page here")

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCorePage
        fields = ['name', 'label', 'page_type', 'parent_page',
                  'simple_api', 'search_configs', 'list_configs', 'view_name', 'template_text']

    def __init__(self, *args, **kwargs):
        """Init class and create form helper."""
        super(PageForm, self).__init__(*args, **kwargs)

    def clean(self):
        """clean() is executed when the form is sent to check it. Here, page types are checked against its
        requirements. Example: A simple search needs an API config but no List- and SearchConfiguration."""
        cleaned_data = super().clean()
        page_type = cleaned_data['page_type']
        search_configs = cleaned_data['search_configs']
        list_configs = cleaned_data['list_configs']
        simple_api = cleaned_data['simple_api']

        if page_type == NdrCorePage.PageType.TEMPLATE:
            # no additional fields required
            pass
        elif page_type == NdrCorePage.PageType.SIMPLE_SEARCH:
            if simple_api is None:
                msg = "You must provide an API configuration for Simple Search pages."
                self.add_error('simple_api', msg)
        elif page_type == NdrCorePage.PageType.SEARCH:
            if search_configs.count() == 0:
                msg = "You must provide at least one Search configuration for Search pages."
                self.add_error('search_configs', msg)
        elif page_type == NdrCorePage.PageType.COMBINED_SEARCH:
            if search_configs.count() == 0:
                msg = "You must provide at least one Search configuration for Combined Search pages."
                self.add_error('search_configs', msg)
            if simple_api is None:
                msg = "You must provide an API configuration for Combined Search pages."
                self.add_error('simple_api', msg)
        elif page_type == NdrCorePage.PageType.FILTER_LIST:
            if list_configs.count() == 0:
                msg = "You must provide at least one List configuration for List pages."
                self.add_error('list_configs', msg)
        elif page_type == NdrCorePage.PageType.CONTACT:
            if NdrCorePage.objects.filter(page_type=NdrCorePage.PageType.CONTACT).count() > 0:
                if self.instance.pk is None:
                    msg = "You can't have more than one contact page."
                    self.add_error('page_type', msg)
        else:
            pass

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('name', css_class='form-group col-md-6 mb-0'),
            Column('label', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('view_name', css_class='form-group col-md-6 mb-0'),
            Column('parent_page', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('page_type', css_class='form-group col-md-6 mb-0'),
            Column(
                HTML('<div class="alert alert-info small m-3" role="alert">'
                     '  <i class="fa-regular fa-circle-info"></i>'
                     '  <span id="page_type_info"></span>'
                     '</div>'
                     ),
                css_class='form-group col-md-6 mb-0'
            ),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('simple_api', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('search_configs', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('list_configs', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('template_text', css_class='form-group center col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        return helper


class PageCreateForm(PageForm):
    """Form to create a page. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(PageCreateForm, self).helper
        helper.layout.append(get_form_buttons('Create New Page'))
        return helper


class PageEditForm(PageForm):
    """Form to edit a page. Extends the base form class and adds an 'edit' button."""

    def __init__(self, **kwargs):
        super(PageEditForm, self).__init__(**kwargs)
        if self.initial["view_name"] == "index":
            self.fields['view_name'].disabled = True
            self.fields['view_name'].help_text = "This is your landing page you can\'t change its view name."

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(PageEditForm, self).helper
        helper.layout.append(get_form_buttons('Save Page'))
        return helper


class FooterForm(SettingsListForm):
    """Form to edit the footer settings."""

    def __init__(self, *args, **kwargs):
        kwargs['settings'] = ["footer_show_partners", "footer_show_main_navigation", "footer_show_socials",
                              "footer_copyright_text"]
        super(FooterForm, self).__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = super(FooterForm, self).helper
        layout = helper.layout = Layout()

        form_row = Row(
            Column('save_footer_show_partners', css_class='form-group col-md-10 mb-0'),
            Column(HTML(f'<a href="{reverse("ndr_core:view_images", kwargs={"group": "logos"})}" class="btn btn-sm btn-secondary">Manage Partner Logos</a>'),
                   css_class='form-group col-md-2 mb-0 text-right'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('save_footer_show_main_navigation', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('save_footer_show_socials', css_class='form-group col-md-10 mb-0'),
            Column(HTML(f'<a href="{reverse("ndr_core:view_settings", kwargs={"group": "socials"})}" class="btn btn-sm btn-secondary">Manage Social Links</a>'),
                   css_class='form-group col-md-2 mb-0 text-right'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('save_footer_copyright_text', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)
        layout.append(get_form_buttons('Save Settings'))
        return helper
