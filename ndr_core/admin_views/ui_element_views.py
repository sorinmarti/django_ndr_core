from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from ndr_core.admin_forms.ui_element_forms import UIElementCardCreateForm, UIElementCardEditForm, \
    UIElementSlideshowCreateForm, UIElementSlideshowEditForm, UIElementCarouselEditForm, UIElementCarouselCreateForm, \
    UIElementJumbotronEditForm, UIElementJumbotronCreateForm, UIElementIframeEditForm, UIElementIframeCreateForm, \
    UIElementBannerEditForm, UIElementBannerCreateForm
from ndr_core.models import NdrCoreUIElement, NdrCoreUiElementItem


class ConfigureUIElements(LoginRequiredMixin, View):
    """View to add/edit/delete UI Elements. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'ui_elements': NdrCoreUIElement.objects.all()}

        return render(self.request, template_name='ndr_core/admin_views/configure_ui_elements.html',
                      context=context)


class UIElementDetailView(LoginRequiredMixin, DetailView):
    """TODO """

    model = NdrCoreUIElement
    template_name = 'ndr_core/admin_views/configure_ui_elements.html'

    def get_context_data(self, **kwargs):
        context = super(UIElementDetailView, self).get_context_data(**kwargs)
        context['ui_elements'] = NdrCoreUIElement.objects.all()
        return context


class UIElementCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new NdrCoreUIElement """

    model = NdrCoreUIElement
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/ui_element_create.html'

    def get_form_class(self):
        if self.kwargs['type'] == "card":
            return UIElementCardCreateForm
        elif self.kwargs['type'] == "carousel":
            return UIElementCarouselCreateForm
        elif self.kwargs['type'] == "slideshow":
            return UIElementSlideshowCreateForm
        elif self.kwargs['type'] == "jumbotron":
            return UIElementJumbotronCreateForm
        elif self.kwargs['type'] == "iframe":
            return UIElementIframeCreateForm
        elif self.kwargs['type'] == "banner":
            return UIElementBannerCreateForm
        return None

    def get_context_data(self, **kwargs):
        context = super(UIElementCreateView, self).get_context_data(**kwargs)
        if self.kwargs['type'] == "card":
            context['view_title'] = "Create New Card"
        elif self.kwargs['type'] == "carousel":
            context['view_title'] = "Create New Carousel"
        elif self.kwargs['type'] == "slideshow":
            context['view_title'] = "Create New Slideshow"
        elif self.kwargs['type'] == "jumbotron":
            context['view_title'] = "Create New Jumbotron"
        elif self.kwargs['type'] == "iframe":
            context['view_title'] = "Create New Iframe"
        elif self.kwargs['type'] == "banner":
            context['view_title'] = "Create New Banner"
        return context

    def form_valid(self, form):
        # Creates object and returns HttpResponse
        response = super(UIElementCreateView, self).form_valid(form)

        if self.kwargs['type'] == "card":
            # A Card has 1 item.
            card_item = NdrCoreUiElementItem.objects.create(belongs_to=self.object,
                                                            order_idx=0)
            if self.object.show_image:
                card_item.ndr_image = form.cleaned_data['card_item_image']
            if not self.object.use_image_conf:
                card_item.title = form.cleaned_data['card_item_title']
                card_item.text = form.cleaned_data['card_item_text']
                card_item.url = form.cleaned_data['card_item_url']
                self.object.title = card_item.title
            else:
                self.object.title = card_item.ndr_image.title
            card_item.save()

            self.object.type = NdrCoreUIElement.UIElementType.CARD
            self.object.save()

        elif self.kwargs['type'] == "carousel":
            self.object.type = NdrCoreUIElement.UIElementType.CAROUSEL
            self.object.save()
        elif self.kwargs['type'] == "slideshow":
            # A Slideshow has an item for each image.
            index = 0
            for image in form.cleaned_data['slideshow_images']:
                NdrCoreUiElementItem.objects.create(belongs_to=self.object,
                                                    order_idx=index,
                                                    ndr_image=image)
                index += 1
            self.object.type = NdrCoreUIElement.UIElementType.SLIDESHOW
            self.object.save()
        elif self.kwargs['type'] == "jumbotron":
            self.object.type = NdrCoreUIElement.UIElementType.JUMBOTRON
            self.object.save()

        elif self.kwargs['type'] == "iframe":
            self.object.type = NdrCoreUIElement.UIElementType.IFRAME
            self.object.save()

        elif self.kwargs['type'] == "banner":
            card_item = NdrCoreUiElementItem.objects.create(belongs_to=self.object,
                                                            order_idx=0)
            card_item.ndr_image = form.cleaned_data['card_item_image']
            card_item.save()
            self.object.type = NdrCoreUIElement.UIElementType.BANNER
            self.object.save()

        return response


class UIElementEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing NdrCoreUIElement """

    model = NdrCoreUIElement
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/ui_element_edit.html'

    def get_form_class(self):
        if self.object.type == NdrCoreUIElement.UIElementType.CARD:
            return UIElementCardEditForm
        elif self.object.type == NdrCoreUIElement.UIElementType.CAROUSEL:
            return UIElementCarouselEditForm
        elif self.object.type == NdrCoreUIElement.UIElementType.SLIDESHOW:
            return UIElementSlideshowEditForm
        elif self.object.type == NdrCoreUIElement.UIElementType.JUMBOTRON:
            return UIElementJumbotronEditForm
        elif self.object.type == NdrCoreUIElement.UIElementType.IFRAME:
            return UIElementIframeEditForm
        elif self.object.type == NdrCoreUIElement.UIElementType.BANNER:
            return UIElementBannerEditForm
        print("TYPE", self.object.type)
        return UIElementCardEditForm

    """def get_context_data(self, **kwargs):
        return super(UIElementEditView, self).get_context_data(**kwargs)
        if self.object.type == NdrCoreUIElement.UIElementType.CARD:
            context['view_title'] = "Edit Card"
        elif self.object.type == NdrCoreUIElement.UIElementType.CAROUSEL:
            context['view_title'] = "Edit Carousel"
        elif self.object.type == NdrCoreUIElement.UIElementType.SLIDESHOW:
            context['view_title'] = "Edit Slideshow"
        elif self.object.type == NdrCoreUIElement.UIElementType.JUMBOTRON:
            context['view_title'] = "Edit Jumbotron"
        return context"""


class UIElementDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete an NdrCoreUIElement from the database. """

    model = NdrCoreUIElement
    success_url = reverse_lazy('ndr_core:configure_ui_elements')
    template_name = 'ndr_core/admin_views/ui_element_confirm_delete.html'

