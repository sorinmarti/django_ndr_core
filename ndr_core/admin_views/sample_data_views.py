import os
import re

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from ndr_core.models import NdrCoreColorScheme, NdrCoreValue, NdrCoreUiStyle
from ndr_core.ndr_settings import NdrSettings

class SampleDataView(LoginRequiredMixin, View):
    """ View to manage sample data jsons """

    def get(self, request, *args, **kwargs):
        data_dir = os.listdir('ndr/static/ndr/sample_data')
        for data in data_dir:
            print(data)
        return render(self.request,
                      template_name='ndr_core/admin_views/configure_sample_data.html',
                      context={})