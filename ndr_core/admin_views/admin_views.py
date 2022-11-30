"""Contains basic views used in the NDRCore admin interface."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command
from django.shortcuts import render, redirect
from django.views import View

from ndr_core.models import NdrCorePage, NdrCoreSearchConfiguration, NdrCoreValue, NdrCoreApiConfiguration, \
    NdrCoreUiStyle, NdrCoreColorScheme
from ndr_core.ndr_settings import NdrSettings


class NdrCoreDashboard(LoginRequiredMixin, View):
    """The NDR Core dashboard is the start page of the admin interface. It shows your pages and your options. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        try:
            ui_style = NdrCoreUiStyle.objects.get(name=NdrCoreValue.objects.get(value_name='ui_style').value_value).label
        except NdrCoreValue.DoesNotExist:
            ui_style = None

        try:
            color_scheme = NdrCoreColorScheme.objects.get(
                scheme_name=NdrCoreValue.objects.get(value_name='ui_color_scheme').value_value).scheme_label
        except NdrCoreValue.DoesNotExist:
            color_scheme = None

        return render(self.request,
                      template_name='ndr_core/admin_views/dashboard.html',
                      context={'ndr_inizialized': NdrSettings.app_exists(),
                               'ndr_registered': NdrSettings.app_registered(),
                               'ndr_in_urls': NdrSettings.app_in_urls(),
                               'numbers': {
                                   'api': NdrCoreApiConfiguration.objects.all().count(),
                                   'search': NdrCoreSearchConfiguration.objects.all().count(),
                                   'page': NdrCorePage.objects.all().count(),
                                   'messages': 0
                               },
                               'ui_style': ui_style,
                               'color_scheme': color_scheme})


class HelpView(LoginRequiredMixin, View):
    """TODO """
    def get(self, request, *args, **kwargs):
        chapter = None
        if "chapter" in kwargs:
            chapter = kwargs["chapter"]
        return render(self.request,
                      template_name='ndr_core/admin_views/help.html',
                      context={'chapter': chapter})


def init_ndr_core(request):
    """TODO """
    if not NdrSettings.app_exists():
        call_command('init_ndr_core')
        messages.success(request, "NDR Core application initialized.")
    else:
        messages.error(request, "NDR Core application already exists.")
    return redirect('ndr_core:dashboard')