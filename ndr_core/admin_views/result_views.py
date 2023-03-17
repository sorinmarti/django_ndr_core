from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, FormView

from ndr_core.admin_forms.result_forms import RenderConfigurationForm, MyTestForm
from ndr_core.models import NdrCoreSearchConfiguration
from ndr_core.admin_forms.api_forms import ApiCreateForm, ApiEditForm
from ndr_core.models import NdrCoreApiConfiguration


class ConfigureResultsView(LoginRequiredMixin, View):
    """View to add/edit/delete API configurations. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'searches': NdrCoreSearchConfiguration.objects.all().order_by('conf_label'),
                   'form': RenderConfigurationForm(),
                   't_form': MyTestForm()}

        return render(self.request, template_name='ndr_core/admin_views/configure_results.html',
                      context=context)

    def post(self, request, *args, **kwargs):
        values = {"last_name": "Caesar", "first_name": "Julius", "age": 44, "battles": ["Alesia", "Pharsalus"],
                  "various": {"a": 1, "b": 2, "c": 3}, "date": "2019-01-01"}
        form = MyTestForm(self.request.POST)
        if form.is_valid():
            print("VALID")
            print(form.cleaned_data)
            format_string = form.cleaned_data['format_field']
            print(format_string)
            print(format_string.format(**values))

        context = {'searches': NdrCoreSearchConfiguration.objects.all().order_by('conf_label'),
                   'form': RenderConfigurationForm(),
                   't_form': MyTestForm()}

        return render(self.request, template_name='ndr_core/admin_views/configure_results.html',
                      context=context)

class ResultsConfigurationDetailView(LoginRequiredMixin, FormView):

    template_name = 'ndr_core/admin_views/configure_results.html'

    def get(self, request, *args, **kwargs):
        """GET request for this view. """
        conf_name = kwargs['search_config']
        context = {'searches': NdrCoreSearchConfiguration.objects.all().order_by('conf_label'),
                   'configuration': NdrCoreSearchConfiguration.objects.get(conf_name=conf_name),
                   'form': RenderConfigurationForm()}
        return render(self.request, template_name='ndr_core/admin_views/configure_results.html',
                      context=context)

    def form_valid(self, form):

        return super().form_valid(form)

