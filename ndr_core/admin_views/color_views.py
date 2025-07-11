"""Views for the color palette management. """
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.core.serializers.base import DeserializationError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    FormView
)
from ndr_core.admin_forms.color_forms import (
    ColorPaletteCreateForm,
    ColorPaletteEditForm,
    ColorPaletteImportForm
)
from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.models import NdrCoreColorScheme, NdrCoreValue
from ndr_core.ndr_settings import NdrSettings


class ConfigureColorPalettes(AdminViewMixin, LoginRequiredMixin, View):
    """View to add/edit/delete Color Palettes. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """
        value = NdrCoreValue.objects.get(value_name='ui_color_scheme')

        palettes = NdrCoreColorScheme.objects.all().order_by('scheme_label')
        try:
            palette = NdrCoreColorScheme.objects.get(scheme_name=value.value_value)
        except NdrCoreColorScheme.DoesNotExist:
            palette = palettes.first()

        context = {'palettes': palettes,
                   'palette':  palette}

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_colors.html',
                      context=context)


class ColorPaletteDetailView(AdminViewMixin, LoginRequiredMixin, DetailView):
    """View to show details about a color palette. """

    model = NdrCoreColorScheme
    template_name = 'ndr_core/admin_views/overview/configure_colors.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['palettes'] = NdrCoreColorScheme.objects.all().order_by('scheme_label')
        value = NdrCoreValue.objects.get(value_name='ui_color_scheme')
        context['palette'] = NdrCoreColorScheme.objects.get(scheme_name=value.value_value)
        return context


class ColorPaletteCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """ View to create a new Color Palette """

    model = NdrCoreColorScheme
    form_class = ColorPaletteCreateForm
    success_url = reverse_lazy('ndr_core:configure_colors')
    template_name = 'ndr_core/admin_views/create/palette_create.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class ColorPaletteEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """ View to edit an existing Color Palette """

    model = NdrCoreColorScheme
    form_class = ColorPaletteEditForm
    success_url = reverse_lazy('ndr_core:configure_colors')
    template_name = 'ndr_core/admin_views/edit/palette_edit.html'


class ColorPaletteDeleteView(AdminViewMixin, LoginRequiredMixin, DeleteView):
    """ View to delete a Color Palette from the database. Asks to confirm."""

    model = NdrCoreColorScheme
    success_url = reverse_lazy('ndr_core:configure_colors')
    template_name = 'ndr_core/admin_views/delete/palette_confirm_delete.html'


class ColorPaletteImportView(AdminViewMixin, LoginRequiredMixin, FormView):
    """View to import a exported color palette. """

    template_name = 'ndr_core/admin_views/import/palette_import.html'
    form_class = ColorPaletteImportForm
    success_url = reverse_lazy('ndr_core:configure_colors')

    def form_valid(self, form):
        f = form.files['palette_file']

        try:
            my_string = f.read().decode('utf-8')
            deserialized_object = serializers.deserialize("json", "["+my_string+"]")
            for obj in deserialized_object:
                if NdrCoreColorScheme.objects.filter(scheme_name=obj.object.scheme_name).count() > 0:
                    messages.info(self.request, f'The scheme "{obj.object.scheme_name}" was updated')
        except DeserializationError:
            messages.error(self.request, 'Could not deserialize object.')

        return super().form_valid(form)


@login_required
def choose_color_palette(request, pk):
    """ Function to select the project's used color palette. """

    try:
        palette = NdrCoreColorScheme.objects.get(pk=pk)
        value = NdrCoreValue.get_or_initialize(value_name='ui_color_scheme',
                                               init_label='NDR Core Color Scheme')
        value.value_value = palette.scheme_name
        value.save()

        color_template_path = "static/ndr_core/app_init/color_template.css"
        if os.path.isfile(color_template_path):
            with open(color_template_path, "r+", encoding='utf8') as color_in_file:
                text = color_in_file.read()
                for color_name in NdrCoreColorScheme.color_list():
                    text = text.replace(f"[[{color_name}]]", getattr(palette, color_name))

                color_output_path = f"{NdrSettings.get_css_path()}/colors.css"
                if os.path.isfile(color_output_path):
                    os.remove(color_output_path)
                with open(color_output_path, "w", encoding='utf8') as color_out_file:
                    color_out_file.write(text)

    except NdrCoreColorScheme.DoesNotExist:
        messages.error(request, 'Color scheme to set not found!')

    return redirect('ndr_core:view_palette', pk=pk)
