"""Views for the search field configuration pages. """
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.form_preview import get_search_form_image_from_raw_data
from ndr_core.admin_forms.search_field_forms import SearchFieldCreateForm, SearchFieldEditForm

from ndr_core.models import NdrCoreSearchField


class SearchFieldCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """ View to create a new Search Field """

    model = NdrCoreSearchField
    form_class = SearchFieldCreateForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/create/search_field_create.html'


class SearchFieldEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """ View to edit an existing Search field """

    model = NdrCoreSearchField
    form_class = SearchFieldEditForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/edit/search_field_edit.html'


class SearchFieldDeleteView(AdminViewMixin, LoginRequiredMixin, DeleteView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    model = NdrCoreSearchField
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/delete/search_field_confirm_delete.html'


def preview_search_form_image(request, img_config):
    """Creates a form preview image of a search form configuration. """

    data = []
    config_rows = img_config.split(",")
    for row in config_rows:
        config_row = row.split("~")
        if '' not in config_row:
            field = NdrCoreSearchField.objects.get(pk=config_row[3])
            data.append({
                'row': int(config_row[0]),
                'col': int(config_row[1]),
                'size': int(config_row[2]),
                'text': field.field_label,
                'type': field.field_type})
    image_data = get_search_form_image_from_raw_data(data)
    return HttpResponse(image_data, content_type="image/png")
