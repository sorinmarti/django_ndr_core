from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.core.serializers.base import DeserializationError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, FormView

from ndr_core.admin_forms.color_forms import ColorPaletteCreateForm, ColorPaletteEditForm, ColorPaletteImportForm
from ndr_core.models import NdrCoreColorScheme, NdrCoreValue


class ConfigureColorPalettes(LoginRequiredMixin, View):
    """View to add/edit/delete Color Palettes. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """
        value = NdrCoreValue.objects.get(value_name='ui_color_scheme')
        context = {'palettes': NdrCoreColorScheme.objects.all().order_by('scheme_label'),
                   'palette':  NdrCoreColorScheme.objects.get(scheme_name=value.value_value)}

        return render(self.request, template_name='ndr_core/admin_views/configure_colors.html',
                      context=context)


class ColorPaletteDetailView(LoginRequiredMixin, DetailView):
    """View to show details about a color palette. """

    model = NdrCoreColorScheme
    template_name = 'ndr_core/admin_views/configure_colors.html'

    def get_context_data(self, **kwargs):
        context = super(ColorPaletteDetailView, self).get_context_data(**kwargs)
        context['palettes'] = NdrCoreColorScheme.objects.all().order_by('scheme_label')
        value = NdrCoreValue.objects.get(value_name='ui_color_scheme')
        context['palette'] = NdrCoreColorScheme.objects.get(scheme_name=value.value_value)
        return context


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


class ColorPaletteImportView(LoginRequiredMixin, FormView):
    """View to import a exported color palette. """

    template_name = 'ndr_core/admin_views/palette_import.html'
    form_class = ColorPaletteImportForm
    success_url = reverse_lazy('ndr_core:configure_colors')

    def form_valid(self, form):
        f = form.files['palette_file']

        try:
            my_string = f.read().decode('utf-8')
            deserialized_object = serializers.deserialize("json", "["+my_string+"]")
            for obj in deserialized_object:
                if NdrCoreColorScheme.objects.filter(scheme_name=obj.object.scheme_name).count()>0:
                    messages.info(self.request, f'The scheme "{obj.object.scheme_name}" was updated')
                print(obj.save())
        except DeserializationError:
            messages.error(self.request, 'Could not deserialize object.')

        return super().form_valid(form)


def choose_color_palette(request, pk):
    """ Function to select the project's used color palette. """

    try:
        value = NdrCoreValue.objects.get(value_name='ui_color_scheme')
        palette = NdrCoreColorScheme.objects.get(pk=pk)
        value.value_value = palette.scheme_name
        value.save()
    except NdrCoreValue.DoesNotExist:
        messages.error(request, 'Scheme Setting is Not in Database!')
    except NdrCoreColorScheme.DoesNotExist:
        messages.error(request, 'Color scheme to set not found!')

    return redirect('ndr_core:view_palette', pk=pk)
