from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView

from ndr_core.admin_forms.upload_forms import UploadCreateForm, UploadEditForm
from ndr_core.models import NdrCoreUpload


class ConfigureUploads(LoginRequiredMixin, View):
    """View to add/edit/delete Uploads. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'files': NdrCoreUpload.objects.all()}
        return render(self.request, template_name='ndr_core/admin_views/configure_uploads.html',
                      context=context)


class UploadCreateView(LoginRequiredMixin, CreateView):
    """ View to create a image """

    model = NdrCoreUpload
    form_class = UploadCreateForm
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/upload_create.html'

    def form_valid(self, form):
        response = super(UploadCreateView, self).form_valid(form)
        return response


class UploadEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing image """

    model = NdrCoreUpload
    form_class = UploadEditForm
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/upload_edit.html'

    def form_valid(self, form):
        response = super(UploadEditView, self).form_valid(form)
        return response


class UploadDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete an image from the database. Asks to confirm."""

    model = NdrCoreUpload
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/upload_confirm_delete.html'

    def form_valid(self, form):
        return super(UploadDeleteView, self).form_valid(form)
