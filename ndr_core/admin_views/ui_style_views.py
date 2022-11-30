import os
import re

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from ndr_core.models import NdrCoreColorScheme, NdrCoreValue, NdrCoreUiStyle
from ndr_core.ndr_settings import NdrSettings


class ConfigureUI(LoginRequiredMixin, View):
    """The configure UI view lets you choose a UI style and a color scheme for your installation. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        return render(self.request,
                      template_name='ndr_core/admin_views/configure_ui.html',
                      context=self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Executed when the form is sent. Check if style or color scheme have been changed. Save changes in DB and
        rewrite the base.html file accordingly."""
        new_ui_style = request.POST.get('ui_style', None)
        new_color_scheme = request.POST.get('ui_color_scheme', None)
        changed_values = False

        # Check if UI Style has changed
        if new_ui_style is not None:
            setting = NdrCoreValue.get_or_initialize('ui_style')
            # The UI style has changed: Save in DB and rewrite base.html file
            if new_ui_style != setting.value_value:
                error_message = None
                new_file_str = None
                base_filename = f'{NdrSettings.APP_NAME}/templates/{NdrSettings.APP_NAME}/base.html'
                if os.path.isfile(base_filename):
                    with open(base_filename, 'r') as base_file:
                        file_str = base_file.read()
                        match = re.match(r'^\{\% extends [\"\']ndr_core/base/styles/base\_(.*)[\"\'] \%\}', file_str)
                        if match is not None and len(match.groups()) > 0:
                            new_file_str = file_str.replace(match.groups()[0], f'{new_ui_style}.html')
                        else:
                            error_message = "Pattern to replace not found"

                    if new_file_str is not None:
                        with open(base_filename, 'w') as new_base_file:
                            new_base_file.write(new_file_str)
                            setting.value_value = new_ui_style
                            setting.save()
                            changed_values = True
                else:
                    error_message = "Base file not found"

                if error_message is not None:
                    messages.error(request, error_message)

        # Check if Color Scheme has changed
        if new_color_scheme is not None:
            setting = NdrCoreValue.get_or_initialize('ui_color_scheme')
            # The Color scheme has changed: Save in DB and...
            if new_color_scheme != setting.value_value:
                error_message = None
                style_filename = finders.find('ndr_core/app_init/color_template.css')
                color_scheme = NdrCoreColorScheme.objects.get(scheme_name=new_color_scheme)
                if os.path.isfile(style_filename):
                    with open(style_filename, 'r') as style_file:
                        file_str = style_file.read()
                        keys = [('background_color', color_scheme.background_color),
                                ('text_color', color_scheme.text_color),
                                ('button_color', color_scheme.button_color),
                                ('button_hover_color', color_scheme.button_hover_color),
                                ('button_text_color', color_scheme.button_text_color),
                                ('button_border_color', color_scheme.button_border_color),
                                ('second_button_color', color_scheme.second_button_color),
                                ('second_button_hover_color', color_scheme.second_button_border_color),
                                ('second_button_text_color', color_scheme.second_button_text_color),
                                ('second_button_border_color', color_scheme.second_button_border_color),
                                ('link_color', color_scheme.link_color),
                                ('accent_color_1', color_scheme.accent_color_1),
                                ('accent_color_2', color_scheme.accent_color_2),
                                ('info_color', color_scheme.info_color),
                                ('success_color', color_scheme.success_color),
                                ('error_color', color_scheme.error_color)]
                        for key in keys:
                            file_str = file_str.replace(f"[[{key[0]}]]", key[1])

                    if file_str is not None:
                        new_style_filename = f'{NdrSettings.APP_NAME}/static/{NdrSettings.APP_NAME}/css/colors.css'
                        with open(new_style_filename, 'w') as new_style_file:
                            new_style_file.write(file_str)
                            setting.value_value = new_color_scheme
                            setting.save()
                            changed_values = True
                else:
                    error_message = "Style file not found"

                if error_message is not None:
                    messages.error(request, error_message)

        if changed_values:
            messages.info(request, "Settings saved")

        return render(self.request,
                      template_name='ndr_core/admin_views/configure_ui.html',
                      context=self.get_context_data())

    @staticmethod
    def get_context_data(**kwargs):
        """Returns the context data for both GET and POST request. """
        ui_list = NdrCoreUiStyle.objects.all().order_by('name')
        palette_list = NdrCoreColorScheme.objects.all().order_by('scheme_name')
        current_style = NdrCoreValue.get_or_initialize('ui_style', init_value='default').value_value
        current_palette = NdrCoreValue.get_or_initialize('ui_color_scheme', init_value='default').value_value
        return {'ui_styles': ui_list,
                'palettes': palette_list,
                'current_style': current_style,
                'current_palette': current_palette}