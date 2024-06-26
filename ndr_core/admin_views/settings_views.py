"""Views for the Settings section of the admin panel."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.core.serializers.base import DeserializationError
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView, FormView

from ndr_core.admin_forms.settings_forms import (
    SettingsListForm,
    SettingCreateForm,
    SettingEditForm,
    SettingsImportForm,
    SettingsSetReadonlyForm,
    SettingsSetEditableForm,
    SettingsSetUnderConstructionForm,
    SettingsSetLiveForm,
)
from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.models import NdrCoreValue

settings_group_list = {
            'page': {
                'name': 'page',
                'title': 'Page Settings',
                'help_text': 'These settings are not mandatory but recommended.',
                'settings': ['under_construction',
                             'under_construction_text',
                             'project_title',
                             'header_default_title']
             },
            'language': {
                'name': 'language',
                'title': 'Language Settings',
                'help_text': 'Select the language you create your content in. Then select all languages you want to '
                             'translate your content to.',
                'settings': ['ndr_language',
                             'available_languages']
            },
            'header': {
                'name': 'header',
                'title': 'Header Settings',
                'help_text': 'These settings help search engines find you.',
                'settings': ['header_description',
                             'header_author']
            },
            'search': {
                'name': 'search',
                'title': 'Search Settings',
                'help_text': 'Settings for your search',
                'settings': ['search_allow_download_single',
                             'search_allow_download_list_json',
                             'search_allow_download_list_csv',
                             'search_download_max_results']
            },
            'mail': {
                'name': 'mail',
                'title': 'Mail Settings',
                'help_text': 'To use the contact form, you need to provide your mail settings. '
                             'Only unauthenticated settings for now.',
                'settings': ['messages_behaviour',
                             'contact_form_default_subject',
                             'email_config_host',
                             'contact_form_send_to_address',
                             'contact_form_send_from_address',
                             'contact_form_display_captcha']
            },
            'socials': {
                'name': 'socials',
                'title': 'Social Media',
                'help_text': 'If you fill in the social media links and activate social media links in your footer '
                             'configuration, they will be displayed in your footer.',
                'settings': ['socials_twitter',
                             'socials_instagram',
                             'socials_facebook',
                             'socials_mastodon']
            },
            'custom': {
                'name': 'custom',
                'title': 'Custom Settings',
                'help_text': 'These are settings you created yourself.',
                'settings': []
            }
        }


class ConfigureSettingsView(AdminViewMixin, LoginRequiredMixin, TemplateView):
    """View to view and change value settings of NDR Core (such as HTML page title tags, etc.). """

    template_name = 'ndr_core/admin_views/overview/configure_settings.html'

    @staticmethod
    def get_context_data():
        """Returns the context data for both GET and POST request. """

        context = {'settings_list': settings_group_list}
        return context


class SettingsDetailView(AdminViewMixin, LoginRequiredMixin, View):
    """Shows a group of settings to change in a form. """

    template_name = 'ndr_core/admin_views/configure_settings.html'
    settings_list = None
    settings_form = None
    settings_group = None

    def get_context_data(self):
        """Returns the context data for this view."""
        settings_group = settings_group_list[self.kwargs['group']]
        # Users can create their own settings, which are identified by is_user_value=True
        if settings_group['name'] == "custom":
            settings_list = NdrCoreValue.objects.filter(is_user_value=True).values_list('value_name', flat=True)
            settings_form = SettingsListForm(settings=settings_list,
                                             is_custom_form=True)
        # All other settings that are used by NDR Core are configured and added to groups upon project creation
        else:
            settings_form = SettingsListForm(settings=settings_group['settings'])

        context = {'settings_list': settings_group_list,
                   'object': settings_group,
                   'form': settings_form}
        return context

    def get(self, request, *args, **kwargs):
        """GET request for this view. """
        return render(self.request,
                      template_name='ndr_core/admin_views/overview/configure_settings.html',
                      context=self.get_context_data())

    def post(self, request, *args, **kwargs):
        """POST request for this view. Gets executed when setting values are saved."""
        context = self.get_context_data()
        form = SettingsListForm(request.POST, settings=settings_group_list[self.kwargs['group']]['settings'])
        form.save_list()

        context['form'] = form

        messages.success(request, "Saved Changes")
        return render(self.request,
                      template_name='ndr_core/admin_views/overview/configure_settings.html',
                      context=context)


class SettingCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """ View to create a new Custom Setting """

    object = None
    model = NdrCoreValue
    form_class = SettingCreateForm
    success_url = reverse_lazy('ndr_core:view_settings', kwargs={'group': 'custom'})
    template_name = 'ndr_core/admin_views/create/setting_create.html'

    def form_valid(self, form):
        self.object = form.save(False)
        self.object.is_user_value = True
        self.object.save()
        return super().form_valid(form)


class SettingEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """ View to edit an existing user_setting """

    model = NdrCoreValue
    form_class = SettingEditForm
    success_url = reverse_lazy('ndr_core:view_settings', kwargs={'group': 'custom'})
    template_name = 'ndr_core/admin_views/edit/setting_edit.html'


class SettingDeleteView(AdminViewMixin, LoginRequiredMixin, DeleteView):
    """ View to delete a user setting from the database. Asks to confirm."""

    model = NdrCoreValue
    success_url = reverse_lazy('ndr_core:view_settings', kwargs={'group': 'custom'})
    template_name = 'ndr_core/admin_views/delete/setting_confirm_delete.html'


class SettingsImportView(AdminViewMixin, LoginRequiredMixin, FormView):
    """View to import a exported color palette. """

    template_name = 'ndr_core/admin_views/import/settings_import.html'
    form_class = SettingsImportForm
    success_url = reverse_lazy('ndr_core:configure_settings')

    def form_valid(self, form):
        """When the form is valid, the settings are imported."""
        f = form.files['settings_file']

        try:
            my_string = f.read().decode('utf-8')
            deserialized_object = serializers.deserialize("json", my_string)
            for obj in deserialized_object:
                if NdrCoreValue.objects.filter(value_name=obj.object.value_name).count() > 0:
                    messages.info(self.request, f'The setting "{obj.object.value_name}" was updated')
        except DeserializationError:
            messages.error(self.request, 'Could not deserialize object.')

        return super().form_valid(form)


class SetPageReadOnlyView(AdminViewMixin, LoginRequiredMixin, FormView):
    """View to set the page read-only."""

    template_name = "ndr_core/admin_views/page_state/settings_set_readonly.html"
    form_class = SettingsSetReadonlyForm
    success_url = reverse_lazy("ndr_core:configure_settings")

    def form_valid(self, form):
        """When the page is set to read-only, the page is set to read-only."""
        NdrCoreValue.objects.filter(value_name='page_is_editable').update(value_value='false')
        return super().form_valid(form)


class SetPageEditableView(AdminViewMixin, LoginRequiredMixin, FormView):
    """View to set the page editable. """

    template_name = "ndr_core/admin_views/page_state/settings_set_readonly.html"
    form_class = SettingsSetEditableForm
    success_url = reverse_lazy("ndr_core:configure_settings")

    def form_valid(self, form):
        """When the page is set to editable, the page is set to read-only."""
        NdrCoreValue.objects.filter(value_name='page_is_editable').update(value_value='true')
        return super().form_valid(form)


class SetPageUnderConstructionView(AdminViewMixin, LoginRequiredMixin, FormView):
    """View to set the page under construction. """

    template_name = "ndr_core/admin_views/page_state/settings_set_under_construction.html"
    form_class = SettingsSetUnderConstructionForm
    success_url = reverse_lazy("ndr_core:configure_settings")

    def form_valid(self, form):
        """When the page is set to under construction, the page is set to read-only."""
        NdrCoreValue.objects.filter(value_name='under_construction').update(value_value='true')
        return super().form_valid(form)


class SetPageLiveView(AdminViewMixin, LoginRequiredMixin, FormView):
    """View to set the page live. """

    template_name = "ndr_core/admin_views/page_state/settings_set_live.html"
    form_class = SettingsSetLiveForm
    success_url = reverse_lazy("ndr_core:configure_settings")

    def form_valid(self, form):
        NdrCoreValue.objects.filter(value_name='under_construction').update(value_value='false')
        return super().form_valid(form)
