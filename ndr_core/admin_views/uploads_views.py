from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView

from ndr_core.admin_forms.upload_forms import (
    UploadCreateForm,
    UploadEditForm,
    ManifestUploadCreateForm,
    ManifestUploadEditForm,
    ManifestGroupCreateForm,
    ManifestGroupEditForm,
)

from ndr_core.models import NdrCoreUpload, NdrCoreManifest, NdrCoreManifestGroup


class ConfigureUploads(LoginRequiredMixin, View):
    """View to add/edit/delete Uploads. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'files': NdrCoreUpload.objects.all(),
                   'manifests': NdrCoreManifest.objects.all()}
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
    """ View to delete an upload from the database. Asks to confirm."""

    model = NdrCoreUpload
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/upload_confirm_delete.html'

    def form_valid(self, form):
        self.object.file.delete()
        return super(UploadDeleteView, self).form_valid(form)


class ManifestUploadCreateView(LoginRequiredMixin, CreateView):
    """ View to create a manifest """

    model = NdrCoreManifest
    form_class = ManifestUploadCreateForm
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/manifest_upload_create.html'

    def form_valid(self, form):
        response = super(ManifestUploadCreateView, self).form_valid(form)
        return response


class ManifestUploadEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing manifest """

    model = NdrCoreManifest
    form_class = ManifestUploadEditForm
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/manifest_upload_edit.html'

    def form_valid(self, form):
        response = super(ManifestUploadEditView, self).form_valid(form)
        return response


class ManifestUploadDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete an image from the database. Asks to confirm."""

    model = NdrCoreManifest
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/manifest_upload_confirm_delete.html'

    def form_valid(self, form):
        self.object.file.delete()
        return super(ManifestUploadDeleteView, self).form_valid(form)


class ManifestGroupCreateView(LoginRequiredMixin, CreateView):
    """ View to create a manifest """

    model = NdrCoreManifestGroup
    form_class = ManifestGroupCreateForm
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/manifest_group_create.html'

    def form_valid(self, form):
        response = super(ManifestGroupCreateView, self).form_valid(form)
        return response


class ManifestGroupEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing manifest """

    model = NdrCoreManifestGroup
    form_class = ManifestGroupEditForm
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/manifest_group_edit.html'

    def form_valid(self, form):
        response = super(ManifestGroupEditView, self).form_valid(form)
        return response


class ManifestGroupDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete an image from the database. Asks to confirm."""

    model = NdrCoreManifestGroup
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/manifest_group_confirm_delete.html'

    def form_valid(self, form):
        return super(ManifestGroupDeleteView, self).form_valid(form)
