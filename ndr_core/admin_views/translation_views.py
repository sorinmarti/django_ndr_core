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
)
from ndr_core.models import NdrCoreTranslation, NdrCoreValue


def get_available_languages():
    languages = NdrCoreValue.objects.get(value_name='available_languages').get_value()
    available_languages = []
    for lang in languages:
        info = get_language_info(lang)
        available_languages.append((lang, info['name_local']))
    return available_languages


class ConfigureTranslations(LoginRequiredMixin, View):
    """View to add/edit/delete Translations. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'files': NdrCoreTranslation.objects.filter(table_name='NdrCorePage')}
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class SelectPageTranslationView(View):

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'available_languages': get_available_languages() }
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class SelectFieldTranslationView(View):

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'available_languages': get_available_languages()}
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class SelectSettingsTranslationView(View):

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'available_languages': get_available_languages()}
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class SelectFormTranslationView(View):

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'available_languages': get_available_languages()}
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
                      context=context)


class TranslateView(View):

    def get_context_data(self):
        context = {'available_languages': get_available_languages(),
                   'selected_language': self.kwargs.get('lang', 'en')}
        return context


class TranslatePageValuesView(TranslateView):

    def get(self, request, *args, **kwargs):
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

    def get(self, request, *args, **kwargs):
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

    def get(self, request, *args, **kwargs):
        form = TranslateSettingsForm(lang=self.kwargs.get('lang', 'en'))
        context = self.get_context_data()
        context['form'] = form
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_translations.html',
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

    def get(self, request, *args, **kwargs):
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