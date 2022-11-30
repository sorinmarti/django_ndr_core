from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView


class ConfigureCorrections(LoginRequiredMixin, View):
    """View to add/edit/delete Corrections. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {}
        return render(self.request, template_name='ndr_core/admin_views/configure_corrections.html',
                      context=context)