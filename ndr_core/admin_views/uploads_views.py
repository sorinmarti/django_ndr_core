"""Views for the Uploads section of the admin panel. """
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
from ndr_core.admin_views.admin_views import AdminViewMixin

from ndr_core.models import NdrCoreUpload, NdrCoreManifest, NdrCoreManifestGroup


class ConfigureUploads(AdminViewMixin, LoginRequiredMixin, View):
    """View to add/edit/delete Uploads. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'files': NdrCoreUpload.objects.all(),
                   'manifests': NdrCoreManifest.objects.all()}
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_uploads.html',
                      context=context)


class UploadCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """ View to create an image """

    model = NdrCoreUpload
    form_class = UploadCreateForm
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/create/upload_create.html'


class UploadEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """ View to edit an existing image """

    model = NdrCoreUpload
    form_class = UploadEditForm
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/edit/upload_edit.html'


class UploadDeleteView(AdminViewMixin, LoginRequiredMixin, DeleteView):
    """ View to delete an upload from the database. Asks to confirm."""

    model = NdrCoreUpload
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/delete/upload_confirm_delete.html'

    def form_valid(self, form):
        self.object.file.delete()
        return super().form_valid(form)


class ManifestUploadCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """ View to create a manifest """

    model = NdrCoreManifest
    form_class = ManifestUploadCreateForm
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/create/manifest_upload_create.html'


class ManifestUploadEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """ View to edit an existing manifest """

    model = NdrCoreManifest
    form_class = ManifestUploadEditForm
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/edit/manifest_upload_edit.html'


class ManifestUploadDeleteView(AdminViewMixin, LoginRequiredMixin, DeleteView):
    """ View to delete an image from the database. Asks to confirm."""

    model = NdrCoreManifest
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/delete/manifest_upload_confirm_delete.html'

    def form_valid(self, form):
        self.object.file.delete()
        return super().form_valid(form)


class ManifestGroupCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """ View to create a manifest """

    model = NdrCoreManifestGroup
    form_class = ManifestGroupCreateForm
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/create/manifest_group_create.html'


class ManifestGroupEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """ View to edit an existing manifest """

    model = NdrCoreManifestGroup
    form_class = ManifestGroupEditForm
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/edit/manifest_group_edit.html'

    def form_valid(self, form):
        """Edit the manifest group and all its manifests."""
        response = super().form_valid(form)
        return response


class ManifestGroupDeleteView(AdminViewMixin, LoginRequiredMixin, DeleteView):
    """ View to delete an image from the database. Asks to confirm."""

    model = NdrCoreManifestGroup
    success_url = reverse_lazy('ndr_core:configure_uploads')
    template_name = 'ndr_core/admin_views/delete/manifest_group_confirm_delete.html'
