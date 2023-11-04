from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, FormView

from ndr_core.admin_forms.result_card_forms import SearchConfigurationResultEditForm
from ndr_core.form_preview import get_search_form_image_from_raw_data
from ndr_core.admin_forms.result_field_forms import ResultFieldCreateForm, ResultFieldEditForm
from ndr_core.models import NdrCoreResultField, NdrCoreSearchConfiguration, NdrCoreResultFieldCardConfiguration


class ResultFieldCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new Search Field """

    model = NdrCoreResultField
    form_class = ResultFieldCreateForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/create/result_field_create.html'

    def form_valid(self, form):
        response = super(ResultFieldCreateView, self).form_valid(form)
        return response


class ResultFieldEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing Search field """

    model = NdrCoreResultField
    form_class = ResultFieldEditForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/edit/result_field_edit.html'


class ResultFieldDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    model = NdrCoreResultField
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/delete/result_field_confirm_delete.html'

    def form_valid(self, form):
        return super(ResultFieldDeleteView, self).form_valid(form)


class SearchConfigurationResultEditView(LoginRequiredMixin, FormView):

    form_class = SearchConfigurationResultEditForm
    template_name = 'ndr_core/admin_views/edit/result_card_edit.html'
    success_url = reverse_lazy('ndr_core:configure_search')

    @staticmethod
    def get_row_fields(row):
        return [f'result_field_{row}', f'row_field_{row}', f'column_field_{row}', f'size_field_{row}']

    def get_form(self, form_class=None):
        form = super(SearchConfigurationResultEditView, self).get_form(form_class=form_class)
        fields = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk']).result_card_fields.all()

        form_row = 0
        for field in fields:
            form.fields[f'result_field_{form_row}'].initial = field.result_field
            form.fields[f'row_field_{form_row}'].initial = field.field_row
            form.fields[f'column_field_{form_row}'].initial = field.field_column
            form.fields[f'size_field_{form_row}'].initial = field.field_size
            form_row += 1

        return form

    def form_valid(self, form):
        """Creates or updates the result card configuration for a search configuration. """
        response = super(SearchConfigurationResultEditView, self).form_valid(form)
        conf_object = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk'])

        for row in range(20):
            fields = self.get_row_fields(row)
            if all(field in form.cleaned_data for field in fields) and \
                    all(form.cleaned_data[x] is not None for x in fields):

                # There is a valid row of configuration. Check if it already exists in the database.
                try:
                    updatable_obj = conf_object.result_card_fields.get(result_field=form.cleaned_data[f'result_field_{row}'])
                    updatable_obj.field_row = form.cleaned_data[f'row_field_{row}']
                    updatable_obj.field_column = form.cleaned_data[f'column_field_{row}']
                    updatable_obj.field_size = form.cleaned_data[f'size_field_{row}']
                    updatable_obj.save()
                except NdrCoreResultFieldCardConfiguration.DoesNotExist:
                    new_field = NdrCoreResultFieldCardConfiguration.objects.create(
                        result_field=form.cleaned_data[f'result_field_{row}'],
                        field_row=form.cleaned_data[f'row_field_{row}'],
                        field_column=form.cleaned_data[f'column_field_{row}'],
                        field_size=form.cleaned_data[f'size_field_{row}'])
                    conf_object.result_card_fields.add(new_field)
        return response


def preview_result_card_image(request, img_config):
    """Creates a result card preview image of a result form configuration. """
    data = []
    config_rows = img_config.split(",")
    for row in config_rows:
        config_row = row.split("~")
        if '' not in config_row:
            field = NdrCoreResultField.objects.get(pk=config_row[3])
            data.append({
                'row': int(config_row[0]),
                'col': int(config_row[1]),
                'size': int(config_row[2]),
                'text': '',
                'type': field.field_type})
    image_data = get_search_form_image_from_raw_data(data)
    return HttpResponse(image_data, content_type="image/png")
