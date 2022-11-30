from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from ndr_core.admin_forms import ColorPaletteCreateForm, ColorPaletteEditForm
from ndr_core.models import NdrCoreColorScheme


class ConfigureColorPalettes(LoginRequiredMixin, View):
    """View to add/edit/delete Color Palettes. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'palettes': NdrCoreColorScheme.objects.all().order_by('scheme_label')}

        return render(self.request, template_name='ndr_core/admin_views/configure_colors.html',
                      context=context)


class ColorPaletteDetailView(LoginRequiredMixin, DetailView):
    """TODO """

    model = NdrCoreColorScheme
    template_name = 'ndr_core/admin_views/configure_colors.html'


class ColorPaletteCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new Search Field """

    model = NdrCoreColorScheme
    form_class = ColorPaletteCreateForm
    success_url = reverse_lazy('ndr_core:configure_colors')
    template_name = 'ndr_core/admin_views/palette_create.html'

    def form_valid(self, form):
        response = super(ColorPaletteCreateView, self).form_valid(form)
        return response


class ColorPaletteEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing Search field """

    model = NdrCoreColorScheme
    form_class = ColorPaletteEditForm
    success_url = reverse_lazy('ndr_core:configure_colors')
    template_name = 'ndr_core/admin_views/palette_edit.html'


class ColorPaletteDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    model = NdrCoreColorScheme
    success_url = reverse_lazy('ndr_core:configure_colors')
    template_name = 'ndr_core/admin_views/palette_confirm_delete.html'

    def form_valid(self, form):
        return super(ColorPaletteDeleteView, self).form_valid(form)
