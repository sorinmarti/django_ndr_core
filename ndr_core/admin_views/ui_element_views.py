from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from ndr_core.admin_forms.ui_element_forms import UIElementEditForm, UIElementCreateForm
from ndr_core.models import NdrCoreUIElement


class ConfigureUIElements(LoginRequiredMixin, View):
    """View to add/edit/delete UI Elements. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {}

        return render(self.request, template_name='ndr_core/admin_views/configure_ui_elements.html',
                      context=context)


class UIElementDetailView(LoginRequiredMixin, DetailView):
    """TODO """

    model = NdrCoreUIElement
    template_name = 'ndr_core/admin_views/configure_ui_elements.html'


class UIElementCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new NdrCoreUIElement """

    model = NdrCoreUIElement
    form_class = UIElementCreateForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/ui_element_create.html'


class UIElementEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing NdrCoreUIElement """

    model = NdrCoreUIElement
    form_class = UIElementEditForm
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/ui_element_edit.html'


class UIElementDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete an NdrCoreUIElement from the database. """

    model = NdrCoreUIElement
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/ui_element_confirm_delete.html'

