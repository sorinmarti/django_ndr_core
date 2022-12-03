import os
import re

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, FormView

from ndr_core.admin_forms.images_forms import ImageUploadForm, LogoUploadForm
from ndr_core.models import NdrCoreColorScheme, NdrCoreValue, NdrCoreUiStyle
from ndr_core.ndr_settings import NdrSettings


class ConfigureImages(LoginRequiredMixin, View):
    """View to add/edit/delete Images. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'logo_path': f'{NdrSettings.APP_NAME}/images/logo.png'}
        return render(self.request, template_name='ndr_core/admin_views/configure_images.html',
                      context=context)


class ImagesGroupView(LoginRequiredMixin, View):
    """Shows a group of images. """

    template_name = 'ndr_core/admin_views/configure_images.html'

    def get_context_data(self):
        context = {'logo_path': f'{NdrSettings.APP_NAME}/images/logo.png'}
        return context

    def get(self, request, *args, **kwargs):
        return render(self.request,
                      template_name=self.template_name,
                      context=self.get_context_data())


class ImagesUploadView(LoginRequiredMixin, FormView):
    """ View to upload sample json data to an API configuration. """

    template_name = 'ndr_core/admin_views/image_upload.html'
    form_class = ImageUploadForm
    success_url = reverse_lazy('ndr_core:configure_images')

    def form_valid(self, form):
        return super().form_valid(form)


class LogoUploadView(LoginRequiredMixin, FormView):
    """ View to upload sample json data to an API configuration. """

    template_name = 'ndr_core/admin_views/logo_upload.html'
    form_class = LogoUploadForm
    success_url = reverse_lazy('ndr_core:configure_images')

    def form_valid(self, form):
        return super().form_valid(form)
