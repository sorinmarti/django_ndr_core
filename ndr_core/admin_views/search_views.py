from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from ndr_core.form_preview import get_search_form_image_from_raw_data
from ndr_core.admin_forms.search_field_forms import SearchFieldCreateForm, SearchFieldEditForm
from ndr_core.admin_forms.search_forms import (
    SearchConfigurationEditForm,
    SearchConfigurationCreateForm,
)
from ndr_core.models import NdrCoreSearchField, NdrCoreSearchConfiguration, \
    NdrCoreSearchFieldFormConfiguration, NdrCoreResultField


class ConfigureSearch(LoginRequiredMixin, View):
    """View to add/edit/delete Search configurations. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        search_fields = NdrCoreSearchField.objects.all()
        result_fields = NdrCoreResultField.objects.all()
        searches = NdrCoreSearchConfiguration.objects.all()
        context = {'search_fields': search_fields,
                   'result_fields': result_fields,
                   'searches': searches}

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_search.html',
                      context=context)


class SearchConfigurationCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new API configuration """

    model = NdrCoreSearchConfiguration
    form_class = SearchConfigurationCreateForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/create/search_config_create.html'

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
    form_class = SearchConfigurationEditForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/edit/search_config_edit.html'

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
        response = super(SearchConfigurationEditView, self).form_valid(form)
        return response


class SearchConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    model = NdrCoreSearchConfiguration
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/delete/search_config_confirm_delete.html'

    def form_valid(self, form):
        return super(SearchConfigurationDeleteView, self).form_valid(form)


class SearchConfigurationFormEditView(LoginRequiredMixin, View):
    pass

class SearchConfigurationResultEditView(LoginRequiredMixin, View):
    pass