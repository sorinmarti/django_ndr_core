"""Contains all views used in the NDRCore admin interface."""
import os.path
import re
import shutil

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView

from ndr_core.form_preview import get_image_from_raw_data
from ndr_core.admin_forms import SearchConfigurationForm, PageCreateForm, SettingsForm, \
    PageEditForm, ApiCreateForm, ApiEditForm, SearchFieldCreateForm, SearchFieldEditForm, SettingCreateForm
from ndr_core.models import NdrCorePage, NdrCoreDataSchema, NdrCoreSearchField, NdrCoreSearchConfiguration, \
    NdrCoreValue, NdrCoreApiConfiguration, NdrCoreSearchFieldFormConfiguration, NdrCoreUiStyle, NdrCoreColorScheme
from ndr_core.admin_tables import SearchFieldTable
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


class ManagePages(LoginRequiredMixin, View):
    """The ManagePages view shows a table of all pages in an installation and lets you define their order. You can
      edit, delete and create pages here. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'pages': NdrCorePage.objects.all().order_by('index')}

        return render(self.request,
                      template_name='ndr_core/admin_views/configure_pages.html',
                      context=context)


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


class ConfigureSettings(LoginRequiredMixin, View):
    """View to change value settings of NDR Core (such as HTML page title tags, etc.). """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = self.get_context_data()

        return render(self.request,
                      template_name='ndr_core/admin_views/configure_settings.html',
                      context=context)

    def post(self, request, *args, **kwargs):
        """POST request for this view. Gets executed when setting values are saved."""

        save_key = 'save_'
        for key in request.POST.keys():
            value = request.POST.get(key)
            if key.startswith(save_key):
                key = key[len(save_key):]
                v_object = NdrCoreValue.objects.get(value_name=key)
                v_object.value_value = value
                v_object.save()

        messages.success(request, "Saved Changes")
        context = self.get_context_data()
        return render(self.request,
                      template_name='ndr_core/admin_views/configure_settings.html',
                      context=context)

    @staticmethod
    def get_context_data():
        """Returns the context data for both GET and POST request. """

        basic_settings = SettingsForm(settings=['project_title',
                                                'header_default_title',
                                                'header_description',
                                                'header_author'])
        contact_form = SettingsForm(settings=['contact_form_default_subject',
                                              'email_config_host',
                                              'contact_form_send_to_address',
                                              'contact_form_send_from_address'])

        context = {'basic_settings_form': basic_settings,
                   'contact_form': contact_form}

        return context


class SettingCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new Custom Setting """

    model = NdrCoreValue
    form_class = SettingCreateForm
    success_url = reverse_lazy('ndr_core:configure_settings')
    template_name = 'ndr_core/admin_views/setting_create.html'


class ConfigureImages(LoginRequiredMixin, View):
    """View to add/edit/delete Images. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {}
        return render(self.request, template_name='ndr_core/admin_views/configure_images.html',
                      context=context)


class ConfigureCorrections(LoginRequiredMixin, View):
    """View to add/edit/delete Corrections. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {}
        return render(self.request, template_name='ndr_core/admin_views/configure_corrections.html',
                      context=context)


class ConfigureMessages(LoginRequiredMixin, View):
    """View to add/edit/delete Messages. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {}

        return render(self.request, template_name='ndr_core/admin_views/configure_messages.html',
                      context=context)


class ConfigureColorPalettes(LoginRequiredMixin, View):
    """View to add/edit/delete Color Palettes. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {}

        return render(self.request, template_name='ndr_core/admin_views/configure_colors.html',
                      context=context)


class ConfigureUIElements(LoginRequiredMixin, View):
    """View to add/edit/delete UI Elements. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {}

        return render(self.request, template_name='ndr_core/admin_views/configure_ui_elements.html',
                      context=context)


class ConfigureApi(LoginRequiredMixin, View):
    """View to add/edit/delete API configurations. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'apis': NdrCoreApiConfiguration.objects.all().order_by('api_name')}

        return render(self.request, template_name='ndr_core/admin_views/configure_api.html',
                      context=context)


class ConfigureSearch(LoginRequiredMixin, View):
    """View to add/edit/delete Search configurations. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        schemas = NdrCoreDataSchema.objects.all()
        search_fields = NdrCoreSearchField.objects.all()
        searches = NdrCoreSearchConfiguration.objects.all()
        context = {'schemas': schemas, 'search_fields': search_fields, 'searches': searches}

        return render(self.request, template_name='ndr_core/admin_views/configure_search.html',
                      context=context)


# PAGES----------------------------------------------------------------------------------------------------------------
class PageCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new NdrCorePage """

    model = NdrCorePage
    form_class = PageCreateForm
    success_url = reverse_lazy('ndr_core:configure_pages')
    template_name = 'ndr_core/admin_views/page_create.html'

    def form_valid(self, form):
        """Overwrites form_valid function of CreateView. Sets the index of the newly created page object and creates
         a template to save in the ndr apps template folder."""

        response = super(PageCreateView, self).form_valid(form)

        max_index = NdrCorePage.objects.aggregate(Max('index'))
        new_index = max_index["index__max"] + 1
        self.object.index = new_index
        self.object.save()

        new_filename = f'{NdrSettings.APP_NAME}/templates/{NdrSettings.APP_NAME}/{form.cleaned_data["view_name"]}.html'
        if os.path.isfile(new_filename):
            messages.error(self.request, "The file name already existed. No new template was generated.")
        else:
            if self.object.page_type == self.object.PageType.TEMPLATE:
                base_file = finders.find('ndr_core/app_init/template.html')
                shutil.copyfile(base_file, new_filename)
            elif self.object.page_type == self.object.PageType.SIMPLE_SEARCH:
                base_file = finders.find('ndr_core/app_init/search.html')
                shutil.copyfile(base_file, new_filename)
            elif self.object.page_type == self.object.PageType.SEARCH:
                base_file = finders.find('ndr_core/app_init/search.html')
                shutil.copyfile(base_file, new_filename)
            elif self.object.page_type == self.object.PageType.COMBINED_SEARCH:
                base_file = finders.find('ndr_core/app_init/combined_search.html')
                shutil.copyfile(base_file, new_filename)
            elif self.object.page_type == self.object.PageType.FILTER_LIST:
                base_file = finders.find('ndr_core/app_init/filtered_list.html')
                shutil.copyfile(base_file, new_filename)
            elif self.object.page_type == self.object.PageType.CONTACT:
                base_file = finders.find('ndr_core/app_init/contact.html')
                shutil.copyfile(base_file, new_filename)
        return response


class PageEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing NdrCorePage """

    model = NdrCorePage
    form_class = PageEditForm
    success_url = reverse_lazy('ndr_core:configure_pages')
    template_name = 'ndr_core/admin_views/page_edit.html'

    def form_valid(self, form):
        """Overwrites form_valid function of CreateView. Sets the index of the newly created page object and creates
        a template to save in the ndr apps template folder.
            TODO Recreate the template"""

        response = super(PageEditView, self).form_valid(form)
        return response


class PageDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete an NdrCorePage from the database. Asks to confirm.
    This function also deletes the created HTML template. """

    model = NdrCorePage
    success_url = reverse_lazy('ndr_core:configure_pages')
    template_name = 'ndr_core/admin_views/page_confirm_delete.html'

    def form_valid(self, form):
        """Overwrites form_valid function of DeleteView. Deletes the object and its template."""

        filename = f'{NdrSettings.APP_NAME}/templates/{NdrSettings.APP_NAME}/{self.object.view_name}.html'
        if os.path.isfile(filename):
            os.remove(filename)
        else:
            messages.warning(self.request, "HTML template to delete was not found.")

        return super(PageDeleteView, self).form_valid(form)


# API CONFIGURATION----------------------------------------------------------------------------------------------------
class ApiConfigurationCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new API configuration """

    model = NdrCoreApiConfiguration
    form_class = ApiCreateForm
    success_url = reverse_lazy('ndr_core:configure_api')
    template_name = 'ndr_core/admin_views/api_create.html'

    def form_valid(self, form):
        response = super(ApiConfigurationCreateView, self).form_valid(form)

        for row in range(20):
            # TODO Check and create rendering fields
            pass

        return response


class ApiConfigurationEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing API configuration """

    model = NdrCoreApiConfiguration
    form_class = ApiEditForm
    success_url = reverse_lazy('ndr_core:configure_api')
    template_name = 'ndr_core/admin_views/api_edit.html'

    def form_valid(self, form):
        response = super(ApiConfigurationEditView, self).form_valid(form)

        for row in range(20):
            # TODO Check and create/update/delete rendering fields
            pass

        return response


class ApiConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete an API configuration from the database. Asks to confirm."""

    model = NdrCoreApiConfiguration
    success_url = reverse_lazy('ndr_core:configure_api')
    template_name = 'ndr_core/admin_views/api_confirm_delete.html'

    def form_valid(self, form):
        return super(ApiConfigurationDeleteView, self).form_valid(form)


# SEARCH FIELDS--------------------------------------------------------------------------------------------------------
class ConfigureSearchFields(LoginRequiredMixin, View):
    """ View to configure Search Fields. Displays the configured fields and a list of  """

    def get(self, request, *args, **kwargs):
        return render(self.request,
                      template_name='ndr_core/admin_views/configure_search_fields.html',
                      context=self.get_context_data())

    def get_context_data(self, **kwargs):
        context = dict()
        context["json_schemas"] = NdrCoreDataSchema.objects.all()
        context["search_field_table"] = SearchFieldTable(data=NdrCoreSearchField.objects.all())
        return context


class SearchFieldConfigurationCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new Search Field """

    model = NdrCoreSearchField
    form_class = SearchFieldCreateForm
    success_url = reverse_lazy('ndr_core:configure_search_fields')
    template_name = 'ndr_core/admin_views/search_field_create.html'

    def form_valid(self, form):
        response = super(SearchFieldConfigurationCreateView, self).form_valid(form)
        return response


class SearchFieldConfigurationEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing Search field """

    model = NdrCoreSearchField
    form_class = SearchFieldEditForm
    success_url = reverse_lazy('ndr_core:configure_search_fields')
    template_name = 'ndr_core/admin_views/search_field_edit.html'


class SearchFieldConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    model = NdrCoreSearchField
    success_url = reverse_lazy('ndr_core:configure_search_fields')
    template_name = 'ndr_core/admin_views/search_field_confirm_delete.html'

    def form_valid(self, form):
        return super(SearchFieldConfigurationDeleteView, self).form_valid(form)


@login_required
def create_search_fields(request, schema_pk):
    """ Creates a list of NdrCoreSearchField objects based on a schema definition.
    Available search fields depend on the data one wants to access. They can be added manually but also depending
    on an existing data schema if it is known to ndr_core.

        :param request: The page's request object
        :param schema_pk: The primary key of the schema object to create search fields from
        :return: A redirect response to to 'configure_search_fields'
    """

    try:
        schema = NdrCoreDataSchema.objects.get(id=schema_pk)
        existing_fields = NdrCoreSearchField.objects.filter(schema_name=schema.schema_name)
        if existing_fields.count() > 0:
            messages.warning(request, "Existing fields have been overwritten")
            existing_fields.delete()
        call_command('loaddata', schema.fixture_name, app_label='ndr_core')
        messages.success(request, "The Search fields were created")
        return redirect('ndr_core:configure_search')
    except NdrCoreDataSchema.DoesNotExist:
        messages.error(request, "The Schema was not found in the database")
        return redirect('ndr_core:configure_search')


@login_required
def move_page_up(request, pk):
    """ NdrCorePages have an index to determine in which order they are displayed.
    This function moves up a page in the order.

    :param request: The page's request object
    :param pk: The primary key of the NdrCorePage to move up
    :return: A redirect response to to 'configure_pages'
    """

    try:
        page = NdrCorePage.objects.get(id=pk)
        if page.index > 0:
            other_page = NdrCorePage.objects.get(index=page.index-1)
            old_index = page.index
            page.index = page.index - 1
            page.save()
            other_page.index = old_index
            other_page.save()
        else:
            messages.warning(request, "Page is already on top")
    except NdrCorePage.DoesNotExist:
        messages.error(request, "Page does not exist")
    return redirect('ndr_core:configure_pages')


# SEARCH FORM CONFIGURATION--------------------------------------------------------------------------------------------
class SearchConfigurationCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new API configuration """

    model = NdrCoreSearchConfiguration
    form_class = SearchConfigurationForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/search_config_create.html'

    def form_valid(self, form):
        """TODO """

        response = super(SearchConfigurationCreateView, self).form_valid(form)

        for row in range(20):
            if f'search_field_{row}' in form.cleaned_data and \
               f'row_field_{row}' in form.cleaned_data and \
               f'column_field_{row}' in form.cleaned_data and \
               f'size_field_{row}' in form.cleaned_data and \
               form.cleaned_data[f'search_field_{row}'] is not None and \
               form.cleaned_data[f'row_field_{row}'] is not None and \
               form.cleaned_data[f'column_field_{row}'] is not None and  \
               form.cleaned_data[f'size_field_{row}'] is not None:
                new_field = NdrCoreSearchFieldFormConfiguration.objects.create(
                    search_field=form.cleaned_data[f'search_field_{row}'],
                    field_row=form.cleaned_data[f'row_field_{row}'],
                    field_column=form.cleaned_data[f'column_field_{row}'],
                    field_size=form.cleaned_data[f'size_field_{row}'])
                self.object.search_form_fields.add(new_field)

        return response


class SearchConfigurationEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing API configuration """

    model = NdrCoreSearchConfiguration
    form_class = SearchConfigurationForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/search_config_edit.html'


class SearchConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    model = NdrCoreSearchConfiguration
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/search_config_confirm_delete.html'

    def form_valid(self, form):
        return super(SearchConfigurationDeleteView, self).form_valid(form)


class SampleDataView(LoginRequiredMixin, View):
    """ View to manage sample data jsons """

    def get(self, request, *args, **kwargs):
        data_dir = os.listdir('ndr/static/ndr/sample_data')
        for data in data_dir:
            print(data)
        return render(self.request,
                      template_name='ndr_core/admin_views/configure_sample_data.html',
                      context={})

def preview_image(request, img_config):
    """Creates a form preview image of a search form configuration. """

    data = []
    config_rows = img_config.split(",")
    for row in config_rows:
        config_row = row.split("~")
        if '' not in config_row:
            data.append({
                'row': int(config_row[0]),
                'col': int(config_row[1]),
                'size': int(config_row[2]),
                'text': NdrCoreSearchField.objects.get(id=int(config_row[3])).field_label})
    image_data = get_image_from_raw_data(data)
    return HttpResponse(image_data, content_type="image/png")


def init_ndr_core(request):
    if not NdrSettings.app_exists():
        call_command('init_ndr_core')
        messages.success(request, "NDR Core application initialized.")
    else:
        messages.error(request, "NDR Core application already exists.")
    return redirect('ndr_core:dashboard')