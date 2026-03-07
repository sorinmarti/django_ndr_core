"""Views for the UI Element admin pages."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from ndr_core.admin_forms.ui_element_types import (
    CardCreateForm, CardEditForm,
    JumbotronCreateForm, JumbotronEditForm,
    BannerCreateForm, BannerEditForm,
    IFrameCreateForm, IFrameEditForm,
    ManifestViewerCreateForm, ManifestViewerEditForm,
    SlidesCreateForm, SlidesEditForm,
    CarouselCreateForm, CarouselEditForm,
    DataObjectCreateForm, DataObjectEditForm,
    JSModuleCreateForm, JSModuleEditForm,
)
from ndr_core.admin_forms.ui_element_types.video_forms import VideoCreateForm, VideoEditForm
from ndr_core.admin_forms.ui_element_types.audio_forms import AudioCreateForm, AudioEditForm
from ndr_core.admin_forms.ui_element_types.academic_about_forms import AcademicAboutCreateForm, AcademicAboutEditForm
from ndr_core.admin_forms.ui_element_types.team_grid_forms import TeamGridCreateForm, TeamGridEditForm, TeamGridItemFormSet
from ndr_core.admin_forms.ui_element_types.slides_forms import SlidesItemFormSet
from ndr_core.admin_forms.ui_element_types.carousel_forms import CarouselItemFormSet
from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.models import NdrCoreUIElement, NdrCoreImage, NdrCoreUiElementItem


class ConfigureUIElements(AdminViewMixin, LoginRequiredMixin, View):
    """View to manage UI Elements list."""

    def get(self, request, *args, **kwargs):
        context = {'ui_elements': NdrCoreUIElement.objects.all()}
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_ui_elements.html',
                      context=context)


class UIElementShowcaseView(AdminViewMixin, LoginRequiredMixin, View):
    """View to display UI Element types gallery."""

    def get(self, request, *args, **kwargs):
        return render(self.request, template_name='ndr_core/admin_views/overview/ui_element_showcase.html')


class UIElementDetailView(AdminViewMixin, LoginRequiredMixin, DetailView):
    """View to display a single UI Element with preview."""

    model = NdrCoreUIElement
    template_name = 'ndr_core/admin_views/overview/configure_ui_elements.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ui_elements'] = NdrCoreUIElement.objects.all()
        return context


class UIElementDeleteView(AdminViewMixin, LoginRequiredMixin, DeleteView):
    """View to delete a UI Element (works for all types)."""

    model = NdrCoreUIElement
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/delete/ui_element_confirm_delete.html'


# ============================================================================
# Single-Item Type Views (Card, Jumbotron, Banner, IFrame, Manifest Viewer)
# ============================================================================

class CardCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new Card UI Element."""
    model = NdrCoreUIElement
    form_class = CardCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_card_create.html'


class CardEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing Card UI Element."""
    model = NdrCoreUIElement
    form_class = CardEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_card_edit.html'


class JumbotronCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new Jumbotron UI Element."""
    model = NdrCoreUIElement
    form_class = JumbotronCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_jumbotron_create.html'


class JumbotronEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing Jumbotron UI Element."""
    model = NdrCoreUIElement
    form_class = JumbotronEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_jumbotron_edit.html'


class BannerCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new Banner UI Element."""
    model = NdrCoreUIElement
    form_class = BannerCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_banner_create.html'


class BannerEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing Banner UI Element."""
    model = NdrCoreUIElement
    form_class = BannerEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_banner_edit.html'


class IFrameCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new IFrame UI Element."""
    model = NdrCoreUIElement
    form_class = IFrameCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_iframe_create.html'


class IFrameEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing IFrame UI Element."""
    model = NdrCoreUIElement
    form_class = IFrameEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_iframe_edit.html'


class ManifestViewerCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new Manifest Viewer UI Element."""
    model = NdrCoreUIElement
    form_class = ManifestViewerCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_manifest_viewer_create.html'


class ManifestViewerEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing Manifest Viewer UI Element."""
    model = NdrCoreUIElement
    form_class = ManifestViewerEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_manifest_viewer_edit.html'


# ============================================================================
# Multi-Item Type Views (Slides, Carousel, Data Object)
# ============================================================================

class SlidesCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new Slides UI Element with formset."""
    model = NdrCoreUIElement
    form_class = SlidesCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_slides_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = SlidesItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = SlidesItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class SlidesEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing Slides UI Element with formset."""
    model = NdrCoreUIElement
    form_class = SlidesEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_slides_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = SlidesItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = SlidesItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()

            # Check if this was a rename operation (name is PK)
            old_instance_to_delete = getattr(self.object, '_old_instance_to_delete', None)
            if old_instance_to_delete:
                # Clear PKs from formset items so they're created fresh on the new instance
                for formset_form in formset.forms:
                    if formset_form.instance.pk:
                        formset_form.instance.pk = None

            formset.instance = self.object
            formset.save()

            # Delete old instance after formset is saved
            if old_instance_to_delete:
                old_instance_to_delete.delete()

            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CarouselCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new Carousel UI Element with formset."""
    model = NdrCoreUIElement
    form_class = CarouselCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_carousel_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = CarouselItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = CarouselItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CarouselEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing Carousel UI Element with formset."""
    model = NdrCoreUIElement
    form_class = CarouselEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_carousel_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = CarouselItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = CarouselItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()

            # Check if this was a rename operation (name is PK)
            old_instance_to_delete = getattr(self.object, '_old_instance_to_delete', None)
            if old_instance_to_delete:
                # Clear PKs from formset items so they're created fresh on the new instance
                for formset_form in formset.forms:
                    if formset_form.instance.pk:
                        formset_form.instance.pk = None

            formset.instance = self.object
            formset.save()

            # Delete old instance after formset is saved
            if old_instance_to_delete:
                old_instance_to_delete.delete()

            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class TeamGridCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new Team Members Grid UI Element with formset."""
    model = NdrCoreUIElement
    form_class = TeamGridCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_team_grid_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TeamGridItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = TeamGridItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            # Print formset errors for debugging
            print("=== TEAM GRID FORMSET VALIDATION FAILED ===")
            for i, form_errors in enumerate(formset.errors):
                if form_errors:
                    print(f"Form {i} errors:", form_errors)
            print("Non-form errors:", formset.non_form_errors())
            return self.render_to_response(self.get_context_data(form=form))


class TeamGridEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing Team Members Grid UI Element with formset."""
    model = NdrCoreUIElement
    form_class = TeamGridEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_team_grid_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create formset with extra=0 to not show empty forms when editing
        from django.forms import inlineformset_factory
        from ndr_core.admin_forms.ui_element_types.team_grid_forms import TeamGridItemForm
        EditFormSet = inlineformset_factory(
            NdrCoreUIElement,
            NdrCoreUiElementItem,
            form=TeamGridItemForm,
            extra=0,  # No empty forms when editing
            max_num=50,
            can_delete=True,
            can_order=True,
            validate_min=False,
            min_num=0
        )

        if self.request.POST:
            context['formset'] = EditFormSet(self.request.POST, instance=self.object)
        else:
            # Order items by order_idx when loading for editing
            context['formset'] = EditFormSet(
                instance=self.object,
                queryset=self.object.ndrcoreuielementitem_set.all().order_by('order_idx')
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()

            # Check if this was a rename operation (name is PK)
            old_instance_to_delete = getattr(self.object, '_old_instance_to_delete', None)
            if old_instance_to_delete:
                # Clear PKs from formset items so they're created fresh on the new instance
                for formset_form in formset.forms:
                    if formset_form.instance.pk:
                        formset_form.instance.pk = None

            formset.instance = self.object
            formset.save()

            # Delete old instance after formset is saved
            if old_instance_to_delete:
                old_instance_to_delete.delete()

            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class DataObjectCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new Data Object UI Element."""
    model = NdrCoreUIElement
    form_class = DataObjectCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_data_object_create.html'


class DataObjectEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing Data Object UI Element."""
    model = NdrCoreUIElement
    form_class = DataObjectEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_data_object_edit.html'


class VideoCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new Video UI Element."""
    model = NdrCoreUIElement
    form_class = VideoCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_video_create.html'


class VideoEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing Video UI Element."""
    model = NdrCoreUIElement
    form_class = VideoEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_video_edit.html'


class AudioCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new Audio UI Element."""
    model = NdrCoreUIElement
    form_class = AudioCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_audio_create.html'


class AudioEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing Audio UI Element."""
    model = NdrCoreUIElement
    form_class = AudioEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_audio_edit.html'


class AcademicAboutCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new About Me UI Element."""
    model = NdrCoreUIElement
    form_class = AcademicAboutCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_academic_about_create.html'


class AcademicAboutEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing About Me UI Element."""
    model = NdrCoreUIElement
    form_class = AcademicAboutEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_academic_about_edit.html'


class JSModuleCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """View to create a new JavaScript Module UI Element."""
    model = NdrCoreUIElement
    form_class = JSModuleCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_js_module_create.html'


class JSModuleEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """View to edit an existing JavaScript Module UI Element."""
    model = NdrCoreUIElement
    form_class = JSModuleEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_js_module_edit.html'


# ============================================================================
# Helper Functions
# ============================================================================

def get_ndr_image_path(request, pk):
    """Returns the path to an image."""
    try:
        ndr_image = NdrCoreImage.objects.get(pk=pk)
        return HttpResponse(ndr_image.image.url)
    except NdrCoreImage.DoesNotExist:
        return None
