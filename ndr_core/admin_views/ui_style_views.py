import os
import re

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import DetailView

from ndr_core.models import NdrCoreColorScheme, NdrCoreValue, NdrCoreUiStyle
from ndr_core.ndr_settings import NdrSettings


class ConfigureUI(LoginRequiredMixin, View):
    """The configure UI view lets you choose a UI style and a color scheme for your installation. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        value = NdrCoreValue.objects.get(value_name='ui_style')
        context = {'ui_styles': NdrCoreUiStyle.objects.all().order_by('name'),
                   'ui_style': NdrCoreUiStyle.objects.get(name=value.value_value)}

        return render(self.request,
                      template_name='ndr_core/admin_views/configure_ui.html',
                      context=context)


class UIStyleDetailView(LoginRequiredMixin, DetailView):
    """View to show details about a UI style. """

    model = NdrCoreUiStyle
    template_name = 'ndr_core/admin_views/configure_ui.html'

    def get_context_data(self, **kwargs):
        context = super(UIStyleDetailView, self).get_context_data(**kwargs)
        context['ui_styles'] = NdrCoreUiStyle.objects.all().order_by('name')
        value = NdrCoreValue.objects.get(value_name='ui_style')
        context['ui_style'] = NdrCoreUiStyle.objects.get(name=value.value_value)
        return context


def choose_ui_style(request, pk):
    """ Function to select the project's used UI style. """

    try:
        value = NdrCoreValue.objects.get(value_name='ui_style')
        ui_style = NdrCoreUiStyle.objects.get(pk=pk)
        error_message = None
        base_filename = f'{NdrSettings.APP_NAME}/templates/{NdrSettings.APP_NAME}/base.html'
        if os.path.isfile(base_filename):
            with open(base_filename, 'r') as base_file:
                file_str = base_file.read()
                match = re.match(r'^\{\% extends [\"\']ndr_core/base/styles/base\_(.*)[\"\'] \%\}', file_str)
                if match is not None and len(match.groups()) > 0:
                    new_file_str = file_str.replace(match.groups()[0], f'{ui_style.name}.html')
                else:
                    error_message = "Pattern to replace not found"

            if new_file_str is not None:
                with open(base_filename, 'w') as new_base_file:
                    new_base_file.write(new_file_str)
                    value.value_value = ui_style.name
                    value.save()
        else:
            error_message = "Base file not found"

        if error_message is not None:
            messages.error(request, error_message)

    except NdrCoreValue.DoesNotExist:
        messages.error(request, 'UI Style is Not in Database!')
    except NdrCoreColorScheme.DoesNotExist as e:
        messages.error(request, 'UI Style to set not found!')

    return redirect('ndr_core:view_ui_style', pk=pk)
