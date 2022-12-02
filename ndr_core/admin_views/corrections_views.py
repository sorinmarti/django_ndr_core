from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from ndr_core.models import NdrCoreValue


class ConfigureCorrections(LoginRequiredMixin, View):
    """View to add/edit/delete Corrections. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'correction_enabled': True if NdrCoreValue.objects.get(value_name='correction_feature').value_value == "true" else False}
        return render(self.request, template_name='ndr_core/admin_views/configure_corrections.html',
                      context=context)


def set_correction_option(request, option):
    value = NdrCoreValue.objects.get(value_name='correction_feature')
    value.value_value = option
    value.save()
    return redirect('ndr_core:configure_corrections')
