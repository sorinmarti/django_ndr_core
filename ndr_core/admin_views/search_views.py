"""Views for the search configuration pages. """
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, FormView

from ndr_core.admin_forms.search_config_forms import (
    SearchConfigurationCreateForm,
    SearchConfigurationEditForm,
    ExampleResultForm,
)
from ndr_core.admin_forms.search_form_forms import SearchConfigurationFormEditForm
from ndr_core.admin_forms.data_list_filter_forms import DataListFiltersEditForm
from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.models import (
    NdrCoreSearchField,
    NdrCoreSearchConfiguration,
    NdrCoreSearchFieldFormConfiguration,
    NdrCoreResultField
)


class ConfigureSearch(AdminViewMixin, LoginRequiredMixin, View):
    """View to add/edit/delete Search configurations. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        search_fields = NdrCoreSearchField.objects.all().order_by('field_label')
        result_fields = NdrCoreResultField.objects.all().order_by('label')
        searches = NdrCoreSearchConfiguration.objects.all()

        # Build a mapping of which search configurations use each search field
        search_field_usage = {}
        for field in search_fields:
            # Find all SearchFieldFormConfigurations that use this field
            form_configs = NdrCoreSearchFieldFormConfiguration.objects.filter(search_field=field)
            # Find all SearchConfigurations that use these form configs
            used_by = []
            for search_config in searches:
                if search_config.search_form_fields.filter(search_field=field).exists():
                    used_by.append(search_config)
            search_field_usage[field.pk] = used_by

        # Build a mapping of which search configurations use each result field
        result_field_usage = {}
        for field in result_fields:
            # Find all SearchConfigurations that use this result field
            used_by = []
            for search_config in searches:
                if search_config.result_card_fields.filter(result_field=field).exists():
                    used_by.append(search_config)
            result_field_usage[field.pk] = used_by

        context = {'search_fields': search_fields,
                   'result_fields': result_fields,
                   'searches': searches,
                   'search_field_usage': search_field_usage,
                   'result_field_usage': result_field_usage}

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_search.html',
                      context=context)


class SearchConfigurationCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """ View to create a new API configuration """

    model = NdrCoreSearchConfiguration

    form_class = SearchConfigurationCreateForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/create/search_config_create.html'


class SearchConfigurationEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """ View to edit an existing API configuration """

    model = NdrCoreSearchConfiguration
    form_class = SearchConfigurationEditForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/edit/search_config_edit.html'


class SearchConfigurationDeleteView(AdminViewMixin, LoginRequiredMixin, DeleteView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    model = NdrCoreSearchConfiguration
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/delete/search_config_confirm_delete.html'


class SearchConfigurationCopyView(AdminViewMixin, LoginRequiredMixin, View):
    """ View to copy a Search configuration. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        search_conf = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk'])
        search_conf.conf_name = f'{search_conf.conf_name}_copy'
        search_conf.conf_label = f'{search_conf.conf_label} (Copy)'
        search_conf.save()

        return redirect('ndr_core:configure_search')


class SearchConfigurationFormEditView(AdminViewMixin, LoginRequiredMixin, FormView):
    """ View to edit the form configuration for a search configuration. """

    form_class = SearchConfigurationFormEditForm
    template_name = 'ndr_core/admin_views/edit/search_form_edit.html'
    success_url = reverse_lazy('ndr_core:configure_search')

    def get_context_data(self, **kwargs):
        """Passes available fields and current placement JSON to the template."""
        import json
        context = super().get_context_data(**kwargs)
        conf = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk'])
        context['search_configuration'] = conf

        # All search fields for the palette
        all_fields = NdrCoreSearchField.objects.all().order_by('field_label')
        context['available_fields_json'] = json.dumps([
            {'id': f.pk, 'label': f.field_label} for f in all_fields
        ])

        # Current placement state
        placed = conf.search_form_fields.all().order_by('field_row', 'field_column')
        context['initial_config_json'] = json.dumps([
            {
                'field_id': p.search_field.pk,
                'label': p.search_field.field_label,
                'row': p.field_row,
                'col': p.field_column,
                'col_span': p.field_size,
                'row_span': 1,
            }
            for p in placed
        ])
        return context

    def form_valid(self, form):
        """Replaces the entire search form configuration from the grid JSON."""
        import json
        response = super().form_valid(form)
        conf = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk'])

        # Clear existing placements
        ids_to_delete = list(conf.search_form_fields.values_list('id', flat=True))
        conf.search_form_fields.clear()
        NdrCoreSearchFieldFormConfiguration.objects.filter(id__in=ids_to_delete).delete()

        # Recreate from grid JSON
        raw = form.cleaned_data.get('grid_config', '') or '[]'
        for item in json.loads(raw):
            new_field = NdrCoreSearchFieldFormConfiguration.objects.create(
                search_field_id=item['field_id'],
                field_row=item['row'],
                field_column=item['col'],
                field_size=item['col_span'],
            )
            conf.search_form_fields.add(new_field)

        return response


class DataListFiltersEditView(AdminViewMixin, LoginRequiredMixin, FormView):
    """View to configure data list filters for a search configuration."""

    form_class = DataListFiltersEditForm
    template_name = 'ndr_core/admin_views/edit/data_list_filters_edit.html'
    success_url = reverse_lazy('ndr_core:configure_search')

    def get_form(self, form_class=None):
        """Returns the form with initial data from the search configuration."""
        form = super().get_form(form_class=form_class)
        search_config = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk'])

        # Set initial selected filters
        form.fields['data_list_filters'].initial = search_config.data_list_filters.all()

        return form

    def get_context_data(self, **kwargs):
        """Add search configuration to context."""
        context = super().get_context_data(**kwargs)
        context['search_config'] = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        """Save the selected data list filters to the search configuration."""
        response = super().form_valid(form)
        search_config = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk'])

        # Update the data list filters
        search_config.data_list_filters.set(form.cleaned_data['data_list_filters'])

        return response


def extract_json_paths(obj, prefix=''):
    """Recursively extract all leaf-level dot/bracket paths from a JSON object."""
    paths = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            full = f'{prefix}.{key}' if prefix else key
            if isinstance(value, (dict, list)):
                paths.extend(extract_json_paths(value, full))
            else:
                paths.append(full)
    elif isinstance(obj, list) and obj:
        # Represent the first element; use [0] notation
        first = obj[0]
        item_prefix = f'{prefix}[0]'
        if isinstance(first, (dict, list)):
            paths.extend(extract_json_paths(first, item_prefix))
        else:
            paths.append(item_prefix)
    return paths


class ExampleResultConfigView(AdminViewMixin, LoginRequiredMixin, View):
    """View to set and edit the example result JSON for a search configuration."""

    template_name = 'ndr_core/admin_views/edit/example_result_edit.html'

    def _get_config(self, pk):
        return NdrCoreSearchConfiguration.objects.get(pk=pk)

    def get(self, request, pk, *args, **kwargs):
        import json
        config = self._get_config(pk)
        form = ExampleResultForm(instance=config)
        initial_raw = json.dumps(config.example_result_json, indent=2) if config.example_result_json else ''
        paths = extract_json_paths(config.example_result_json) if config.example_result_json else []
        return render(request, self.template_name, {
            'form': form,
            'search_config': config,
            'initial_json': initial_raw,
            'extracted_paths': paths,
        })

    def post(self, request, pk, *args, **kwargs):
        import json
        config = self._get_config(pk)
        raw = request.POST.get('example_result_json_raw', '').strip()

        if raw:
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as e:
                form = ExampleResultForm(instance=config)
                paths = extract_json_paths(config.example_result_json) if config.example_result_json else []
                return render(request, self.template_name, {
                    'form': form,
                    'search_config': config,
                    'initial_json': raw,
                    'json_error': str(e),
                    'extracted_paths': paths,
                })
            config.example_result_json = parsed
        else:
            config.example_result_json = None

        config.save(update_fields=['example_result_json'])
        from django.contrib import messages as django_messages
        django_messages.success(request, "Example result JSON saved.")
        return redirect('ndr_core:configure_search')
