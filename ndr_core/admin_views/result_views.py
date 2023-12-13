""" Views for the result fields and result card configuration. """
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, FormView

from ndr_core.admin_forms.result_card_forms import SearchConfigurationResultEditForm
from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.form_preview import PreviewImage
from ndr_core.admin_forms.result_field_forms import ResultFieldCreateForm, ResultFieldEditForm
from ndr_core.models import (
    NdrCoreResultField,
    NdrCoreSearchConfiguration
)


class ResultFieldCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """ View to create a new Search Field """

    model = NdrCoreResultField
    form_class = ResultFieldCreateForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/create/result_field_create.html'


class ResultFieldEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """ View to edit an existing Search field """

    model = NdrCoreResultField
    form_class = ResultFieldEditForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/edit/result_field_edit.html'


class ResultFieldDeleteView(AdminViewMixin, LoginRequiredMixin, DeleteView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    model = NdrCoreResultField
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/delete/result_field_confirm_delete.html'


class SearchConfigurationResultEditView(AdminViewMixin, LoginRequiredMixin, FormView):
    """ View to edit the result card configuration of a search configuration."""

    form_class = SearchConfigurationResultEditForm
    template_name = 'ndr_core/admin_views/edit/result_card_edit.html'
    success_url = reverse_lazy('ndr_core:configure_search')

    @staticmethod
    def get_row_fields(row):
        """Returns the field names for a given row. """
        return [(f'result_field_{row}', 'result_field'),
                (f'row_field_{row}', 'field_row'),
                (f'column_field_{row}', 'field_column'),
                (f'size_field_{row}', 'field_size')]

    @staticmethod
    def get_compact_row_fields(row):
        """Returns the field names for a given row. """
        return [(f'cpct_result_field_{row}', 'result_field'),
                (f'cpct_row_field_{row}', 'field_row'),
                (f'cpct_column_field_{row}', 'field_column'),
                (f'cpct_size_field_{row}', 'field_size')]

    def get_context_data(self, **kwargs):
        """Adds the search configuration to the context. """
        context = super().get_context_data(**kwargs)
        context['search_configuration'] = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk'])
        return context

    def get_form(self, form_class=None):
        """Returns the form for this view. """
        form = super().get_form(form_class=form_class)
        all_fields = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk']).result_card_fields.all()
        normal_fields = all_fields.filter(result_card_group='normal').order_by('field_column').order_by('field_row')
        compact_fields = all_fields.filter(result_card_group='compact').order_by('field_column').order_by('field_row')

        form_row = 0
        for field in normal_fields:
            row_fields = self.get_row_fields(form_row)
            for field_name, model_field in row_fields:
                form.fields[field_name].initial = getattr(field, model_field)
            form_row += 1

        form_row = 0
        for field in compact_fields:
            row_fields = self.get_compact_row_fields(form_row)
            for field_name, model_field in row_fields:
                form.fields[field_name].initial = getattr(field, model_field)
            form_row += 1

        return form

    def form_valid(self, form):
        """Creates or updates the result card configuration for a search configuration. """
        response = super().form_valid(form)
        conf_object = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk'])
        all_fields = conf_object.result_card_fields.all()
        all_fields.delete()

        for row in range(20):
            fields = self.get_row_fields(row)
            field_names = [x[0] for x in fields]

            if all(field in form.cleaned_data for field in field_names) and \
                    all(form.cleaned_data[x] is not None for x in field_names):

                # There is a valid row of configuration. Check if it already exists in the database.
                conf_line, created = conf_object.result_card_fields.get_or_create(
                    result_card_group='normal',
                    result_field=form.cleaned_data[f'result_field_{row}'])

                conf_line.field_row = form.cleaned_data[f'row_field_{row}']
                conf_line.field_column = form.cleaned_data[f'column_field_{row}']
                conf_line.field_size = form.cleaned_data[f'size_field_{row}']
                conf_line.result_card_group = 'normal'
                conf_line.save()

                if created:
                    conf_object.result_card_fields.add(conf_line)

            compact_fields = self.get_compact_row_fields(row)
            compact_field_names = [x[0] for x in compact_fields]

            if all(field in form.cleaned_data for field in compact_field_names) and \
                    all(form.cleaned_data[x] is not None for x in compact_field_names):

                # There is a valid row of configuration. Check if it already exists in the database.
                conf_line, created = conf_object.result_card_fields.get_or_create(
                    result_card_group='compact',
                    result_field=form.cleaned_data[f'cpct_result_field_{row}'])

                conf_line.field_row = form.cleaned_data[f'cpct_row_field_{row}']
                conf_line.field_column = form.cleaned_data[f'cpct_column_field_{row}']
                conf_line.field_size = form.cleaned_data[f'cpct_size_field_{row}']
                conf_line.result_card_group = 'compact'
                conf_line.save()

                if created:
                    conf_object.result_card_fields.add(conf_line)
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
                'text': field.label})
    image_data = PreviewImage().create_result_card_image_from_raw_data(data)
    return HttpResponse(image_data, content_type="image/png")
