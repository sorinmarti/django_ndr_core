from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from ndr_core.admin_forms.api_forms import ApiCreateForm, ApiEditForm
from ndr_core.models import NdrCoreApiConfiguration


class ConfigureApi(LoginRequiredMixin, View):
    """View to add/edit/delete API configurations. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'apis': NdrCoreApiConfiguration.objects.all().order_by('api_name')}

        return render(self.request, template_name='ndr_core/admin_views/configure_api.html',
                      context=context)


class ApiConfigurationDetailView(LoginRequiredMixin, DetailView):
    """ View to show details of an API configuration """

    model = NdrCoreApiConfiguration
    template_name = 'ndr_core/admin_views/configure_api.html'

    def get_context_data(self, **kwargs):
        context = super(ApiConfigurationDetailView, self).get_context_data(**kwargs)
        context['apis'] = NdrCoreApiConfiguration.objects.all().order_by('api_name')
        return context


class ApiConfigurationCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new API configuration """

    model = NdrCoreApiConfiguration
    form_class = ApiCreateForm
    success_url = reverse_lazy('ndr_core:configure_api')
    template_name = 'ndr_core/admin_views/api_create.html'

    def form_valid(self, form):
        response = super(ApiConfigurationCreateView, self).form_valid(form)
        return response


class ApiConfigurationEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing API configuration """

    model = NdrCoreApiConfiguration
    form_class = ApiEditForm
    success_url = reverse_lazy('ndr_core:configure_api')
    template_name = 'ndr_core/admin_views/api_edit.html'

    def form_valid(self, form):
        response = super(ApiConfigurationEditView, self).form_valid(form)
        return response


class ApiConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete an API configuration from the database. Asks to confirm."""

    model = NdrCoreApiConfiguration
    success_url = reverse_lazy('ndr_core:configure_api')
    template_name = 'ndr_core/admin_views/api_confirm_delete.html'

    def form_valid(self, form):
        return super(ApiConfigurationDeleteView, self).form_valid(form)
