from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from ndr_core.form_preview import get_image_from_raw_data
from ndr_core.admin_forms.search_forms import SearchConfigurationForm, SearchFieldEditForm, SearchFieldCreateForm
from ndr_core.models import NdrCoreDataSchema, NdrCoreSearchField, NdrCoreSearchConfiguration, \
    NdrCoreSearchFieldFormConfiguration


class ConfigureSearch(LoginRequiredMixin, View):
    """View to add/edit/delete Search configurations. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        schemas = NdrCoreDataSchema.objects.all()
        search_fields = NdrCoreSearchField.objects.all()
        searches = NdrCoreSearchConfiguration.objects.all()
        context = {'schemas': schemas, 'search_fields': search_fields, 'searches': searches}

        return render(self.request, template_name='ndr_core/admin_views/configure_search.html',
                      context=context)


class SearchConfigurationDetailView(LoginRequiredMixin, DetailView):
    """TODO """

    model = NdrCoreSearchConfiguration
    template_name = 'ndr_core/admin_views/configure_search.html'


class SearchConfigurationCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new API configuration """

    model = NdrCoreSearchConfiguration
    form_class = SearchConfigurationForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/search_config_create.html'

    def form_valid(self, form):
        """TODO """

        response = super(SearchConfigurationCreateView, self).form_valid(form)

        for row in range(20):
            if f'search_field_{row}' in form.cleaned_data and \
               f'row_field_{row}' in form.cleaned_data and \
               f'column_field_{row}' in form.cleaned_data and \
               f'size_field_{row}' in form.cleaned_data and \
               form.cleaned_data[f'search_field_{row}'] is not None and \
               form.cleaned_data[f'row_field_{row}'] is not None and \
               form.cleaned_data[f'column_field_{row}'] is not None and  \
               form.cleaned_data[f'size_field_{row}'] is not None:
                print("SF", form.cleaned_data[f'search_field_{row}'])
                new_field = NdrCoreSearchFieldFormConfiguration.objects.create(
                    search_field=form.cleaned_data[f'search_field_{row}'],
                    field_row=form.cleaned_data[f'row_field_{row}'],
                    field_column=form.cleaned_data[f'column_field_{row}'],
                    field_size=form.cleaned_data[f'size_field_{row}'])
                self.object.search_form_fields.add(new_field)

        return response


class SearchConfigurationEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing API configuration """

    model = NdrCoreSearchConfiguration
    form_class = SearchConfigurationForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/search_config_edit.html'

    def get_form(self, form_class=None):
        form = super(SearchConfigurationEditView, self).get_form(form_class=form_class)
        fields = self.object.search_form_fields.all()

        form_row = 0
        for field in fields:
            form.fields[f'search_field_{form_row}'].initial = field.search_field
            form.fields[f'row_field_{form_row}'].initial = field.field_row
            form.fields[f'column_field_{form_row}'].initial = field.field_column
            form.fields[f'size_field_{form_row}'].initial = field.field_size
            form_row += 1

        return form

    def form_valid(self, form):
        return super(SearchConfigurationEditView, self).form_valid(form)


class SearchConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    model = NdrCoreSearchConfiguration
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/search_config_confirm_delete.html'

    def form_valid(self, form):
        return super(SearchConfigurationDeleteView, self).form_valid(form)


class SearchFieldConfigurationDetailView(LoginRequiredMixin, DetailView):
    """TODO """

    model = NdrCoreSearchField
    template_name = 'ndr_core/admin_views/configure_search.html'


class SearchFieldConfigurationCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new Search Field """

    model = NdrCoreSearchField
    form_class = SearchFieldCreateForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/search_field_create.html'

    def form_valid(self, form):
        response = super(SearchFieldConfigurationCreateView, self).form_valid(form)
        return response


class SearchFieldConfigurationEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing Search field """

    model = NdrCoreSearchField
    form_class = SearchFieldEditForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/search_field_edit.html'


class SearchFieldConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    model = NdrCoreSearchField
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/search_field_confirm_delete.html'

    def form_valid(self, form):
        return super(SearchFieldConfigurationDeleteView, self).form_valid(form)


@login_required
def create_search_fields(request, schema_pk):
    """ Creates a list of NdrCoreSearchField objects based on a schema definition.
    Available search fields depend on the data one wants to access. They can be added manually but also depending
    on an existing data schema if it is known to ndr_core.

        :param request: The page's request object
        :param schema_pk: The primary key of the schema object to create search fields from
        :return: A redirect response to to 'configure_search_fields'
    """

    try:
        schema = NdrCoreDataSchema.objects.get(id=schema_pk)
        existing_fields = NdrCoreSearchField.objects.filter(schema_name=schema.schema_name)
        if existing_fields.count() > 0:
            messages.warning(request, "Existing fields have been overwritten")
            existing_fields.delete()
        call_command('loaddata', schema.fixture_name, app_label='ndr_core')
        messages.success(request, "The Search fields were created")
        return redirect('ndr_core:configure_search')
    except NdrCoreDataSchema.DoesNotExist:
        messages.error(request, "The Schema was not found in the database")
        return redirect('ndr_core:configure_search')


def preview_image(request, img_config):
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
    image_data = get_image_from_raw_data(data)
    return HttpResponse(image_data, content_type="image/png")
