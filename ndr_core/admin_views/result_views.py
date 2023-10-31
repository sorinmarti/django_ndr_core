from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from ndr_core.form_preview import get_search_form_image_from_raw_data
from ndr_core.admin_forms.result_field_forms import ResultFieldCreateForm, ResultFieldEditForm
from ndr_core.models import NdrCoreResultField

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
