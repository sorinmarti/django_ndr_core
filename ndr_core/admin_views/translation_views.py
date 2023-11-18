"""Views for the translation functions in the admin panel."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.translation import get_language_info
from django.views import View

from ndr_core.admin_forms.translation_forms import (
    TranslatePageForm,
    TranslateFieldForm,
    TranslateSettingsForm,
    TranslateFormForm,
    TranslateUIElementsForm, TranslateImagesForm
)
from ndr_core.models import NdrCoreTranslation, NdrCoreValue


def get_available_languages():
    """Returns a list of available languages."""

    languages = NdrCoreValue.objects.get(value_name='available_languages').get_value()
    available_languages = []
    for lang in languages:
        info = get_language_info(lang)
        available_languages.append((lang, info['name_local']))
    return available_languages


class SelectTranslationView(LoginRequiredMixin, View):
    """View to add/edit/delete Translations."""

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'available_languages': get_available_languages() }
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class ConfigureTranslations(LoginRequiredMixin, View):
    """View to add/edit/delete Translations. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'files': NdrCoreTranslation.objects.filter(table_name='NdrCorePage')}
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class TranslateView(LoginRequiredMixin, View):
    """View to add/edit/delete Translations."""

    def get_context_data(self):
        """Returns the context data for the view."""
        context = {'available_languages': get_available_languages(),
                   'selected_language': self.kwargs.get('lang', 'en')}
        return context


class TranslatePageValuesView(TranslateView):
    """View to add/edit/delete Translations."""

    def get(self, request, *args, **kwargs):
        """GET request for this view."""
        form = TranslatePageForm(lang=self.kwargs.get('lang', 'en'))
        context = self.get_context_data()
        context['form'] = form

        messages.success(request, "Saved Changes")
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)

    def post(self, request, *args, **kwargs):
        """POST request for this view. Gets executed when values are saved."""

        form = TranslatePageForm(request.POST, lang=self.kwargs.get('lang', 'en'))
        form.save_translations()

        context = self.get_context_data()
        context['form'] = form

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class TranslateFieldValuesView(TranslateView):
    """View to add/edit/delete Translations."""

    def get(self, request, *args, **kwargs):
        """GET request for this view."""
        form = TranslateFieldForm(lang=self.kwargs.get('lang', 'en'))
        context = self.get_context_data()
        context['form'] = form
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)

    def post(self, request, *args, **kwargs):
        """POST request for this view. Gets executed when values are saved."""

        form = TranslateFieldForm(request.POST, lang=self.kwargs.get('lang', 'en'))
        form.save_translations()

        context = self.get_context_data()
        context['form'] = form

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class TranslateSettingsValuesView(TranslateView):
    """View to add/edit/delete Translations."""

    def get(self, request, *args, **kwargs):
        """GET request for this view."""
        form = TranslateSettingsForm(lang=self.kwargs.get('lang', 'en'))
        context = self.get_context_data()
        context['form'] = form
        return render(self.request,
                      template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)

    def post(self, request, *args, **kwargs):
        """POST request for this view. Gets executed when values are saved."""

        form = TranslateSettingsForm(request.POST, lang=self.kwargs.get('lang', 'en'))
        form.save_translations()

        context = self.get_context_data()
        context['form'] = form

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class TranslateFormValuesView(TranslateView):
    """View to add/edit/delete Translations."""

    def get(self, request, *args, **kwargs):
        """GET request for this view."""
        form = TranslateFormForm(lang=self.kwargs.get('lang', 'en'))
        context = self.get_context_data()
        context['form'] = form
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)

    def post(self, request, *args, **kwargs):
        """POST request for this view. Gets executed when values are saved."""

        form = TranslateFormForm(request.POST, lang=self.kwargs.get('lang', 'en'))
        form.save_translations()

        context = self.get_context_data()
        context['form'] = form

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class TranslateUIElementsValuesView(TranslateView):
    """View to add/edit/delete Translations."""

    def get(self, request, *args, **kwargs):
        """GET request for this view."""
        form = TranslateUIElementsForm(lang=self.kwargs.get('lang', 'en'))
        context = self.get_context_data()
        context['form'] = form
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)

    def post(self, request, *args, **kwargs):
        """POST request for this view. Gets executed when values are saved."""

        form = TranslateUIElementsForm(request.POST, lang=self.kwargs.get('lang', 'en'))
        form.save_translations()

        context = self.get_context_data()
        context['form'] = form

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class TranslateImagesValuesView(TranslateView):
    """View to add/edit/delete Translations."""

    def get(self, request, *args, **kwargs):
        """GET request for this view."""
        form = TranslateImagesForm(lang=self.kwargs.get('lang', 'en'))
        context = self.get_context_data()
        context['form'] = form
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)

    def post(self, request, *args, **kwargs):
        """POST request for this view. Gets executed when values are saved."""

        form = TranslateImagesForm(request.POST, lang=self.kwargs.get('lang', 'en'))
        form.save_translations()

        context = self.get_context_data()
        context['form'] = form

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)
