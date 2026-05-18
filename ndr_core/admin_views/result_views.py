""" Views for the result fields and result card configuration. """
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, FormView
from django.shortcuts import redirect

from ndr_core.admin_forms.result_card_forms import SearchConfigurationResultEditForm
from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.form_preview import PreviewImage
from ndr_core.admin_forms.result_field_forms import (
    ResultFieldCreateForm, ResultFieldEditForm,
    TabFieldCreateForm, TabFieldEditForm
)
from ndr_core.models import (
    NdrCoreResultField,
    NdrCoreResultFieldCardConfiguration,
    NdrCoreSearchConfiguration,
    NdrCoreSearchField,
)
from ndr_core.admin_views.search_views import extract_json_paths


def _search_field_hints():
    """Return all NdrCoreSearchField instances for use as field-path hints."""
    return NdrCoreSearchField.objects.all().order_by('field_name')


def _example_paths(result_field=None, search_conf_pk=None):
    """Return extracted paths from the best available example JSON.

    Priority:
    1. Explicitly specified search_conf_pk (from ?search_conf= query param)
    2. First search config that uses this result_field and has example JSON set
    Returns (paths_list, conf_label, conf_pk) or ([], None, None).
    """
    if search_conf_pk:
        try:
            conf = NdrCoreSearchConfiguration.objects.get(pk=search_conf_pk)
            if conf.example_result_json:
                return extract_json_paths(conf.example_result_json), conf.conf_label, conf.conf_name
        except NdrCoreSearchConfiguration.DoesNotExist:
            pass

    if result_field:
        for conf in NdrCoreSearchConfiguration.objects.exclude(example_result_json__isnull=True):
            if conf.result_card_fields.filter(result_field=result_field).exists():
                return extract_json_paths(conf.example_result_json), conf.conf_label, conf.conf_name

    return [], None, None


class ResultFieldCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """ View to create a new Search Field """

    model = NdrCoreResultField
    form_class = ResultFieldCreateForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/create/result_field_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_conf_pk = self.request.GET.get('search_conf')
        paths, conf_label, conf_pk = _example_paths(search_conf_pk=search_conf_pk)
        context['example_json_paths'] = paths
        context['example_conf_label'] = conf_label
        context['example_conf_pk'] = conf_pk
        if not paths:
            context['search_form_fields'] = _search_field_hints()
        return context

    def form_valid(self, form):
        """Handle form submission and check which button was clicked."""
        response = super().form_valid(form)
        messages.success(self.request, "Result field saved successfully.")
        if 'submit_and_continue' in self.request.POST:
            return redirect('ndr_core:edit_result_field', pk=self.object.pk)
        return response


class TabFieldCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """ View to create a new Tab Container Field """

    model = NdrCoreResultField
    form_class = TabFieldCreateForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/create/result_field_create.html'

    def form_valid(self, form):
        """Handle form submission."""
        response = super().form_valid(form)
        messages.success(self.request, "Tab container field saved successfully.")
        if 'submit_and_continue' in self.request.POST:
            # Redirect to the edit page for the newly created object
            return redirect('ndr_core:edit_result_field', pk=self.object.pk)
        return response

    def get_context_data(self, **kwargs):
        """Add context to indicate this is a tab field creation."""
        context = super().get_context_data(**kwargs)
        context['is_tab_field'] = True
        return context


class ResultFieldEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """ View to edit an existing Search field """

    model = NdrCoreResultField
    form_class = ResultFieldEditForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/edit/result_field_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_conf_pk = self.request.GET.get('search_conf')
        paths, conf_label, conf_pk = _example_paths(result_field=self.object, search_conf_pk=search_conf_pk)
        context['example_json_paths'] = paths
        context['example_conf_label'] = conf_label
        context['example_conf_pk'] = conf_pk
        if not paths:
            context['search_form_fields'] = _search_field_hints()
        return context

    def get_form_class(self):
        """Return the appropriate form class based on whether this is a tab container."""
        if self.object and self.object.is_tab_container:
            return TabFieldEditForm
        return ResultFieldEditForm

    def form_valid(self, form):
        """Handle form submission and check which button was clicked."""
        response = super().form_valid(form)
        field_type = "Tab container field" if self.object.is_tab_container else "Result field"
        messages.success(self.request, f"{field_type} updated successfully.")
        if 'submit_and_continue' in self.request.POST:
            # Redirect back to the same edit page
            return redirect('ndr_core:edit_result_field', pk=self.object.pk)
        return response


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

    def get_context_data(self, **kwargs):
        """Passes available fields and current placements to the template."""
        import json
        context = super().get_context_data(**kwargs)
        conf = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk'])
        context['search_configuration'] = conf

        # All result fields for the palette
        all_result_fields = NdrCoreResultField.objects.all().order_by('label')
        context['available_fields_json'] = json.dumps([
            {'id': f.pk, 'label': f.label or str(f)} for f in all_result_fields
        ])

        def _placement_json(group):
            placed = conf.result_card_fields.filter(result_card_group=group).order_by('field_row', 'field_column')
            return json.dumps([
                {
                    'field_id': p.result_field.pk,
                    'label': p.result_field.label or str(p.result_field),
                    'row': p.field_row,
                    'col': p.field_column,
                    'col_span': p.field_column_span,
                    'row_span': p.field_row_span,
                }
                for p in placed
            ])

        context['initial_normal_json']  = _placement_json('normal')
        context['initial_compact_json'] = _placement_json('compact')
        return context

    def form_valid(self, form):
        """Replaces the entire result card configuration from the two grid JSONs."""
        import json
        response = super().form_valid(form)
        conf = NdrCoreSearchConfiguration.objects.get(pk=self.kwargs['pk'])

        # Clear all existing placements
        conf.result_card_fields.all().delete()

        def _create_placements(raw_json, group):
            for item in json.loads(raw_json or '[]'):
                obj = NdrCoreResultFieldCardConfiguration.objects.create(
                    result_field_id=item['field_id'],
                    field_row=item['row'],
                    field_column=item['col'],
                    field_column_span=item['col_span'],
                    field_row_span=item['row_span'],
                    result_card_group=group,
                )
                conf.result_card_fields.add(obj)

        _create_placements(form.cleaned_data.get('grid_config_normal',  ''), 'normal')
        _create_placements(form.cleaned_data.get('grid_config_compact', ''), 'compact')

        return response


def preview_result_card_image(request, img_config):
    """Creates a result card preview image of a result form configuration. """

    data = []
    config_rows = img_config.split(",")
    for row in config_rows:
        config_row = row.split("~")
        if '' not in config_row and len(config_row) >= 6:  # Updated: expect 6 values now
            try:
                field = NdrCoreResultField.objects.get(pk=config_row[0])  # field_id is first
                data.append({
                    'row': int(config_row[1]),  # field_row
                    'col': int(config_row[2]),  # field_column
                    'colspan': int(config_row[3]),  # field_column_span
                    'rowspan': int(config_row[4]),  # field_row_span
                    'text': field.label if hasattr(field, 'label') and field.label else str(field)
                })
            except (NdrCoreResultField.DoesNotExist, ValueError, IndexError):
                # Skip invalid configurations
                continue

    if data:  # Only create image if we have valid data
        image_data = PreviewImage().create_result_card_image_from_raw_data(data)
        return HttpResponse(image_data, content_type="image/png")
    else:
        # Return empty/placeholder image if no valid data
        placeholder_data = [{'row': 1, 'col': 1, 'colspan': 12, 'rowspan': 1, 'text': 'No fields configured'}]
        image_data = PreviewImage().create_result_card_image_from_raw_data(placeholder_data)
        return HttpResponse(image_data, content_type="image/png")


class ResultFieldPreviewView(AdminViewMixin, LoginRequiredMixin, View):
    """AJAX endpoint that renders a rich_expression against the example JSON of a search config.

    POST body (JSON): { "expression": "...", "search_conf": "<conf_name>" }
    Returns an HTML fragment.
    """

    def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return HttpResponse('<span class="text-danger small">Invalid request body.</span>')

        expression = body.get('expression', '').strip()
        search_conf_pk = body.get('search_conf', '').strip()

        if not expression:
            return HttpResponse('<span class="text-muted small">Enter an expression above to see a preview here.</span>')

        # Load example JSON
        example_data = None
        conf_label = None
        if search_conf_pk:
            try:
                conf = NdrCoreSearchConfiguration.objects.get(pk=search_conf_pk)
                example_data = conf.example_result_json
                conf_label = conf.conf_label
            except NdrCoreSearchConfiguration.DoesNotExist:
                pass

        if not example_data:
            return HttpResponse(
                '<span class="text-muted small">'
                '<i class="fa-regular fa-circle-info"></i> '
                'No example data configured for this search. '
                'Set one via <strong>Configure Example Result</strong> to enable preview.'
                '</span>'
            )

        from ndr_core.ndr_templatetags.template_string import TemplateString
        try:
            rendered = TemplateString(expression, example_data, show_errors=True).get_formatted_string()
        except Exception as exc:
            rendered = f'<span class="text-danger small">Render error: {exc}</span>'

        return HttpResponse(rendered)
