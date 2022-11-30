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


class ConfigureMessages(LoginRequiredMixin, View):
    """View to add/edit/delete Messages. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {}

        return render(self.request, template_name='ndr_core/admin_views/configure_messages.html',
                      context=context)