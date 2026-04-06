"""Views for the Uploads section of the admin panel. """
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView

from ndr_core.admin_forms.upload_forms import (
    UploadCreateForm,
    UploadEditForm,
    ManifestUploadCreateForm,
    ManifestUploadEditForm,
    ManifestGroupCreateForm,
    ManifestGroupEditForm,
    ManifestBulkUploadForm,
)
from ndr_core.admin_views.admin_views import AdminViewMixin

from ndr_core.models import NdrCoreUpload, NdrCoreManifest, NdrCoreManifestGroup


class ConfigureUploads(AdminViewMixin, LoginRequiredMixin, View):
    """View to add/edit/delete Uploads. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'files': NdrCoreUpload.objects.all().order_by('-id'),
                   'manifests': NdrCoreManifest.objects.all(),
                   'manifest_groups': NdrCoreManifestGroup.objects.all()}
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_uploads_new.html',
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


class AjaxFileUploadView(LoginRequiredMixin, View):
    """AJAX endpoint for drag-and-drop file uploads."""

    def post(self, request, *args, **kwargs):
        """Handle file upload via AJAX."""
        if not request.FILES.get('file'):
            return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)

        uploaded_file = request.FILES['file']
        title = request.POST.get('title', uploaded_file.name)

        # Create form with the uploaded file
        form = UploadCreateForm(data={'title': title}, files={'file': uploaded_file})

        if form.is_valid():
            upload = form.save()
            return JsonResponse({
                'success': True,
                'file_id': upload.pk,
                'file_name': uploaded_file.name,
                'file_size': upload.get_file_size_display(),
                'file_type': upload.get_file_type(),
                'file_icon': upload.get_file_icon_class(),
                'markup_tag': f'[[file|{upload.pk}]]',
                'is_json': upload.get_file_extension() == 'json',
                'plotly_tag': f'[[plotly|{upload.pk}]]' if upload.get_file_extension() == 'json' else None,
            })
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'error': errors}, status=400)


class ManifestBulkUploadView(AdminViewMixin, LoginRequiredMixin, View):
    """View to upload multiple manifests from a ZIP file."""

    def get(self, request, *args, **kwargs):
        """Display the bulk upload form."""
        form = ManifestBulkUploadForm()
        context = {'form': form}
        return render(request,
                     template_name='ndr_core/admin_views/create/manifest_bulk_upload.html',
                     context=context)

    def post(self, request, *args, **kwargs):
        """Process the ZIP file upload."""
        import zipfile
        import json
        import os
        from django.core.files.base import ContentFile

        form = ManifestBulkUploadForm(request.POST, request.FILES)

        if not form.is_valid():
            context = {'form': form}
            return render(request,
                         template_name='ndr_core/admin_views/create/manifest_bulk_upload.html',
                         context=context)

        # Get or create manifest group
        manifest_group = form.cleaned_data.get('manifest_group')
        new_group_title = form.cleaned_data.get('new_group_title')

        if not manifest_group:
            manifest_group = NdrCoreManifestGroup.objects.create(title=new_group_title)

        zip_file = form.cleaned_data['zip_file']

        # Process results
        results = {
            'success': [],
            'errors': [],
            'group': manifest_group
        }

        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Get all JSON files (excluding macOS metadata)
                json_files = [f for f in zip_ref.namelist()
                             if f.lower().endswith('.json')
                             and not f.startswith('__MACOSX')
                             and not os.path.basename(f).startswith('.')]

                for json_filename in json_files:
                    try:
                        # Read JSON content
                        with zip_ref.open(json_filename) as json_file:
                            manifest_data = json.load(json_file)

                        # Basic IIIF validation
                        if '@context' not in manifest_data:
                            results['errors'].append({
                                'filename': json_filename,
                                'error': 'Missing @context field (not a valid IIIF manifest)'
                            })
                            continue

                        if 'sequences' not in manifest_data and 'items' not in manifest_data:
                            results['errors'].append({
                                'filename': json_filename,
                                'error': 'Missing sequences (v2) or items (v3) field'
                            })
                            continue

                        # Extract metadata
                        identifier = os.path.splitext(os.path.basename(json_filename))[0]

                        # Get title from manifest (try multiple fields)
                        title = None
                        if 'label' in manifest_data:
                            label = manifest_data['label']
                            if isinstance(label, dict):
                                # IIIF v3 multi-language label
                                title = next(iter(label.values()))[0] if label else None
                            elif isinstance(label, list):
                                # IIIF v2 multi-language label
                                title = label[0].get('@value') if label else None
                            elif isinstance(label, str):
                                title = label

                        if not title:
                            title = identifier

                        # Try to extract order values from metadata
                        order_value_1 = None
                        order_value_2 = None
                        order_value_3 = None

                        if 'metadata' in manifest_data and isinstance(manifest_data['metadata'], list):
                            for item in manifest_data['metadata']:
                                if isinstance(item, dict):
                                    label_key = item.get('label', '')
                                    value = item.get('value', '')

                                    # Convert label and value if they're objects/arrays
                                    if isinstance(label_key, (dict, list)):
                                        if isinstance(label_key, dict):
                                            label_key = str(next(iter(label_key.values()), [''])[0] if label_key else '')
                                        else:
                                            label_key = str(label_key[0].get('@value', '') if label_key else '')

                                    if isinstance(value, (dict, list)):
                                        if isinstance(value, dict):
                                            value = str(next(iter(value.values()), [''])[0] if value else '')
                                        else:
                                            value = str(value[0].get('@value', '') if value else '')

                                    label_lower = str(label_key).lower()

                                    # Match against manifest group order titles if available
                                    if manifest_group.order_value_1_title and \
                                       manifest_group.order_value_1_title.lower() in label_lower:
                                        order_value_1 = str(value)
                                    elif manifest_group.order_value_2_title and \
                                         manifest_group.order_value_2_title.lower() in label_lower:
                                        order_value_2 = str(value)
                                    elif manifest_group.order_value_3_title and \
                                         manifest_group.order_value_3_title.lower() in label_lower:
                                        order_value_3 = str(value)

                        # Re-read file content to save
                        with zip_ref.open(json_filename) as json_file:
                            file_content = json_file.read()

                        # Create manifest object
                        manifest = NdrCoreManifest(
                            identifier=identifier,
                            title=title,
                            manifest_group=manifest_group,
                            order_value_1=order_value_1 or '',
                            order_value_2=order_value_2 or '',
                            order_value_3=order_value_3 or ''
                        )

                        # Save file
                        manifest.file.save(
                            os.path.basename(json_filename),
                            ContentFile(file_content),
                            save=False
                        )
                        manifest.save()

                        results['success'].append({
                            'filename': json_filename,
                            'identifier': identifier,
                            'title': title,
                            'manifest': manifest
                        })

                    except json.JSONDecodeError as e:
                        results['errors'].append({
                            'filename': json_filename,
                            'error': f'Invalid JSON: {str(e)}'
                        })
                    except Exception as e:
                        results['errors'].append({
                            'filename': json_filename,
                            'error': f'Error processing file: {str(e)}'
                        })

        except Exception as e:
            form.add_error('zip_file', f'Error extracting ZIP file: {str(e)}')
            context = {'form': form}
            return render(request,
                         template_name='ndr_core/admin_views/create/manifest_bulk_upload.html',
                         context=context)

        # Show results
        context = {'results': results}
        return render(request,
                     template_name='ndr_core/admin_views/create/manifest_bulk_upload_results.html',
                     context=context)


@xframe_options_exempt
def upload_embed_view(request, pk):
    """Serve an uploaded file inline for embedding (e.g. PDF viewer).

    The @xframe_options_exempt decorator removes the X-Frame-Options header so
    the browser's native PDF viewer (which uses internal frames) can load the file.
    """
    upload = get_object_or_404(NdrCoreUpload, pk=pk)
    if not upload.file:
        raise Http404
    return FileResponse(upload.file.open('rb'), as_attachment=False)
