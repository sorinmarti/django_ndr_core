"""Views for the UI Element admin pages. """
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from ndr_core.admin_forms.ui_element_forms import (
    UIElementCreateForm,
    UIElementEditForm
)
from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.models import NdrCoreUIElement, NdrCoreUiElementItem, NdrCoreImage


class ConfigureUIElements(AdminViewMixin, LoginRequiredMixin, View):
    """View to add/edit/delete UI Elements. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'ui_elements': NdrCoreUIElement.objects.all()}

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_ui_elements.html',
                      context=context)


class UIElementDetailView(AdminViewMixin, LoginRequiredMixin, DetailView):
    """TODO """

    model = NdrCoreUIElement
    template_name = 'ndr_core/admin_views/overview/configure_ui_elements.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ui_elements'] = NdrCoreUIElement.objects.all()
        return context


class UIElementCreateView(AdminViewMixin, LoginRequiredMixin, CreateView):
    """ View to create a new NdrCoreUIElement """

    model = NdrCoreUIElement
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/create/ui_element_create.html'
    form_class = UIElementCreateForm

    def form_valid(self, form):
        # Creates object and returns HttpResponse
        response = super().form_valid(form)

        ui_element_type = form.cleaned_data['type']

        if ui_element_type == "card":
            # These are the types that have ONE item.
            card_item = NdrCoreUiElementItem.objects.create(belongs_to=self.object,
                                                            ndr_image=form.cleaned_data['item_0_ndr_card_image'],
                                                            title=form.cleaned_data['item_0_title'],
                                                            text=form.cleaned_data['item_0_text'],
                                                            url=form.cleaned_data['item_0_url'],
                                                            order_idx=0)
            card_item.save()
        elif ui_element_type == "banner":
            # These are the types that have ONE item.
            banner_item = NdrCoreUiElementItem.objects.create(belongs_to=self.object,
                                                              ndr_image=form.cleaned_data['item_0_ndr_banner_image'],
                                                              order_idx=0)
            banner_item.save()
        elif ui_element_type == "iframe":
            # These are the types that have ONE item.
            iframe_item = NdrCoreUiElementItem.objects.create(belongs_to=self.object,
                                                              text=form.cleaned_data['item_0_text'],
                                                              order_idx=0)
            iframe_item.save()
        elif ui_element_type == "jumbotron":
            # These are the types that have ONE item.
            jumbotron_item = NdrCoreUiElementItem.objects.create(belongs_to=self.object,
                                                                 ndr_image=form.cleaned_data['item_0_ndr_banner_image'],
                                                                 title=form.cleaned_data['item_0_title'],
                                                                 text=form.cleaned_data['item_0_text'],
                                                                 url=form.cleaned_data['item_0_url'],
                                                                 order_idx=0)
            jumbotron_item.save()
        elif ui_element_type == "manifest_viewer":
            # These are the types that have ONE item.
            manifest_item = NdrCoreUiElementItem.objects.create(
                belongs_to=self.object,
                manifest_group=form.cleaned_data['item_0_manifest_group'],
                order_idx=0)
            manifest_item.save()
        elif ui_element_type in ["slides", "carousel"]:
            # These are the types that have MULTIPLE items.
            for x in range(0, 10):
                if form.cleaned_data[f'item_{x}_ndr_slide_image'] is not None:
                    slide_item = NdrCoreUiElementItem.objects.create(belongs_to=self.object,
                                                                     ndr_image=form.cleaned_data[f'item_{x}_ndr_slide_image'],
                                                                     title=form.cleaned_data[f'item_{x}_title'],
                                                                     text=form.cleaned_data[f'item_{x}_text'],
                                                                     url=form.cleaned_data[f'item_{x}_url'],
                                                                     order_idx=x)
                    slide_item.save()
                else:
                    pass

        return response


class UIElementEditView(AdminViewMixin, LoginRequiredMixin, UpdateView):
    """ View to edit an existing NdrCoreUIElement """

    model = NdrCoreUIElement
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/edit/ui_element_edit.html'
    form_class = UIElementEditForm


class UIElementDeleteView(AdminViewMixin, LoginRequiredMixin, DeleteView):
    """ View to delete an NdrCoreUIElement from the database. """

    model = NdrCoreUIElement
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/delete/ui_element_confirm_delete.html'


def get_ndr_image_path(request, pk):
    """Returns the path to an image. """

    try:
        ndr_image = NdrCoreImage.objects.get(pk=pk)
        return HttpResponse(ndr_image.image.url)
    except NdrCoreImage.DoesNotExist:
        return None
