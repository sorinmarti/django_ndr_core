import json
import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, FormView

from ndr_core.admin_forms.sample_data_forms import SampleDataUploadForm, SampleDataDeleteForm
from ndr_core.models import NdrCoreApiConfiguration
from ndr_core.ndr_settings import NdrSettings


def get_context_data():
    apis = NdrCoreApiConfiguration.objects.all().order_by('api_name')
    files = {}
    for api in apis:
        dir_name = f'{NdrSettings.get_sample_data_path()}/{api.api_name}'
        if os.path.isdir(dir_name):
            files[api.api_name] = []
            for data in os.listdir(dir_name):
                files[api.api_name].append(data)

    context = {'apis': apis,
               'files': files}
    return context


class SampleDataView(LoginRequiredMixin, View):
    """ View to manage sample data jsons """

    def get(self, request, *args, **kwargs):
        return render(self.request,
                      template_name='ndr_core/admin_views/configure_sample_data.html',
                      context=get_context_data())


class SampleDataDetailView(LoginRequiredMixin, DetailView):
    """View to show details about sample data. """

    model = NdrCoreApiConfiguration
    template_name = 'ndr_core/admin_views/configure_sample_data.html'

    def get_context_data(self, **kwargs):
        file_contents = ""
        file_path = f'{NdrSettings.get_sample_data_path()}/{self.object.api_name}/{self.kwargs["filename"]}'
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                json_result = json.load(f)
                file_contents = json.dumps(json_result, indent=4)

        context = get_context_data()
        context['object'] = self.object
        context['file_name'] = self.kwargs["filename"]
        context['file_contents'] = file_contents
        return context


class SampleDataDeleteView(LoginRequiredMixin, FormView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    template_name = 'ndr_core/admin_views/sample_data_confirm_delete.html'
    form_class = SampleDataDeleteForm
    success_url = reverse_lazy('ndr_core:configure_sample_data')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.kwargs["filename"]
        return context

    def form_valid(self, form):
        file_name = f'{NdrSettings.get_sample_data_path()}/{self.kwargs["pk"]}/{self.kwargs["filename"]}'
        if os.path.exists(file_name):
            os.remove(file_name)
            messages.info(self.request, f'Deleted {self.kwargs["filename"]}')
        return super().form_valid(form)


class SampleDataUploadView(LoginRequiredMixin, FormView):
    """ View to upload sample json data to an API configuration. """

    template_name = 'ndr_core/admin_views/sample_data_upload.html'
    form_class = SampleDataUploadForm
    success_url = reverse_lazy('ndr_core:configure_sample_data')

    def form_valid(self, form):
        f = form.files['upload_file']
        api = form.cleaned_data['api_to_upload_to']
        upload_file = form.cleaned_data['upload_file']
        upload_filename = upload_file.name

        file_dir = f'{NdrSettings.get_sample_data_path()}/{api.api_name}'
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        save_file_path = f'{file_dir}/{upload_filename}'

        # Find new filename
        if not form.cleaned_data['overwrite_files']:
            copy_number = 0
            while os.path.exists(save_file_path):
                did_overwrite = True
                copy_number += 1
                if "." in upload_filename:
                    filename_wo_ending = upload_filename[0:upload_filename.rfind(".")]
                    filename_ending = upload_filename[upload_filename.rfind("."):]
                else:
                    filename_wo_ending = upload_filename
                    filename_ending = ""
                new_filename = f'{filename_wo_ending}_copy_{copy_number:02d}{filename_ending}'
                save_file_path = f'{file_dir}/{new_filename}'

        with open(save_file_path, 'wb+') as destination:
            if form.cleaned_data['overwrite_files'] and os.path.exists(save_file_path):
                messages.info(self.request, f'Replaced {upload_filename}')
            else:
                messages.info(self.request, f'Uploaded {upload_filename}')

            for chunk in f.chunks():
                destination.write(chunk)

        return super().form_valid(form)
