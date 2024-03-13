"""Views for the translation functions in the admin panel."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.models import NdrCoreTranslation, get_available_languages


class SelectTranslationView(AdminViewMixin, LoginRequiredMixin, View):
    """View to add/edit/delete Translations."""

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'available_languages': get_available_languages() }
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class ConfigureTranslations(AdminViewMixin, LoginRequiredMixin, View):
    """View to add/edit/delete Translations. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'files': NdrCoreTranslation.objects.filter(table_name='NdrCorePage')}
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class TranslateView(AdminViewMixin, LoginRequiredMixin, View):
    """View to add/edit/delete Translations."""

    form_class = None

    def __init__(self, form_class=None):
        super().__init__()
        self.form_class = form_class

    def get_context_data(self):
        """Returns the context data for the view."""
        context = {'available_languages': get_available_languages(),
                   'selected_language': self.kwargs.get('lang', 'en')}
        return context

    def get(self, request, *args, **kwargs):
        """GET request for this view."""
        form = self.form_class(lang=self.kwargs.get('lang', 'en'))
        context = self.get_context_data()
        context['form'] = form

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)

    def post(self, request, *args, **kwargs):
        """POST request for this view. Gets executed when values are saved."""

        form = self.form_class(request.POST, lang=self.kwargs.get('lang', 'en'))
        form.save_translations()
        messages.success(request, 'Translations saved successfully.')

        context = self.get_context_data()
        context['form'] = form

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)
