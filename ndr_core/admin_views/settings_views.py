from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from ndr_core.admin_forms.settings_forms import SettingsForm, SettingCreateForm
from ndr_core.models import NdrCoreValue


class ConfigureSettings(LoginRequiredMixin, View):
    """View to change value settings of NDR Core (such as HTML page title tags, etc.). """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = self.get_context_data()

        return render(self.request,
                      template_name='ndr_core/admin_views/configure_settings.html',
                      context=context)

    def post(self, request, *args, **kwargs):
        """POST request for this view. Gets executed when setting values are saved."""

        save_key = 'save_'
        for key in request.POST.keys():
            value = request.POST.get(key)
            if key.startswith(save_key):
                key = key[len(save_key):]
                v_object = NdrCoreValue.objects.get(value_name=key)
                v_object.value_value = value
                v_object.save()

        messages.success(request, "Saved Changes")
        context = self.get_context_data()
        return render(self.request,
                      template_name='ndr_core/admin_views/configure_settings.html',
                      context=context)

    @staticmethod
    def get_context_data():
        """Returns the context data for both GET and POST request. """

        basic_settings = SettingsForm(settings=['project_title',
                                                'header_default_title',
                                                'header_description',
                                                'header_author'])
        contact_form = SettingsForm(settings=['contact_form_default_subject',
                                              'email_config_host',
                                              'contact_form_send_to_address',
                                              'contact_form_send_from_address'])

        context = {'basic_settings_form': basic_settings,
                   'contact_form': contact_form}

        return context


class SettingCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new Custom Setting """

    model = NdrCoreValue
    form_class = SettingCreateForm
    success_url = reverse_lazy('ndr_core:configure_settings')
    template_name = 'ndr_core/admin_views/setting_create.html'
