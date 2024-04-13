"""Views for the search field configuration pages. """
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.form_preview import PreviewImage
from ndr_core.admin_forms.search_field_forms import SearchFieldCreateForm, SearchFieldEditForm
from ndr_core.forms.widgets import CSVTextEditorWidget

from ndr_core.models import NdrCoreSearchField, get_available_languages


class SearchFieldCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """ View to create a new Search Field """

    model = NdrCoreSearchField
    form_class = SearchFieldCreateForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/create/search_field_create.html'

    def get_context_data(self, **kwargs):
        """Adds the CSVTextEditorWidget to the context. """
        context = super().get_context_data(**kwargs)
        context['widget_form'] = CSVTextEditorWidget.ImportCsvForm()
        return context


class SearchFieldEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """ View to edit an existing Search field """

    model = NdrCoreSearchField
    form_class = SearchFieldEditForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/edit/search_field_edit.html'

    def get_context_data(self, **kwargs):
        """Adds the CSVTextEditorWidget to the context. """
        context = super().get_context_data(**kwargs)
        context['widget_form'] = CSVTextEditorWidget.ImportCsvForm()
        return context


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
    image_data = PreviewImage().create_search_form_image_from_raw_data(data)
    return HttpResponse(image_data, content_type="image/png")


def get_field_list_choices(request, field_name):
    """Returns the list choices for a search field. """
    if field_name == 'create':
        return JsonResponse([], safe=False)
    else:
        try:
            field = NdrCoreSearchField.objects.get(pk=field_name)
            return JsonResponse(field.get_choices_list(), safe=False)
        except NdrCoreSearchField.DoesNotExist:
            return JsonResponse({"error": "Field not found."})


def get_field_list_header(request, field_type):
    """Returns the list choices for a search field. """

    header = [
        {'rowHandle': True,
         'formatter': "handle",
         'headerSort': False,
         'frozen': True,
         'width': 30,
         'minWidth': 30},
        get_table_column('Identifier', 'key'),
        get_table_column('Value', 'value')
    ]

    for lang in get_available_languages():
        title = f'Value ({lang[1]})'
        field = f'value_{lang[0]}'
        header.append(get_table_column(title, field))

    if field_type == NdrCoreSearchField.FieldType.LIST or field_type == NdrCoreSearchField.FieldType.MULTI_LIST:
        header.append(get_table_column('Searchable', 'is_searchable', 'tickCross'))
        header.append(get_table_column('Displayable', 'is_printable', 'tickCross'))
    if field_type == NdrCoreSearchField.FieldType.BOOLEAN_LIST:
        header.append(get_table_column('Condition', 'condition', 'tickCross'))

    header.append(get_table_column("Info text", "info"))
    for lang in get_available_languages():
        title = f'Info text ({lang[1]})'
        field = f'info_{lang[0]}'
        header.append(get_table_column(title, field))

    header.append({'title': 'Delete',
                   'formatter': "buttonCross",
                   'width': 40})

    return JsonResponse(header, safe=False)


def get_table_column(title, field, editor='input', editable=True):
    column = {'title': title,
              'field': field,
              'editor': editor,
              'editable': editable}
    return column
