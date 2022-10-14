import os.path
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
from ndr_core.admin_forms import PageForm, ApiForm, SearchFieldForm, SearchConfigurationForm
from ndr_core.models import NdrCorePage, NdrCoreDataSchema, NdrSearchField, SearchConfiguration, NdrCoreValue, \
    ApiConfiguration, SearchFieldFormConfiguration
from ndr_core.admin_tables import PagesTable, SearchConfigurationTable, SettingsTable, ChangeSettingsTable, \
    PagesManageTable, SearchFieldTable, ApiTable
from ndr_core.ndr_settings import NdrSettings


class NdrCoreDashboard(LoginRequiredMixin, View):
    """TODO """

    def get(self, request, *args, **kwargs):
        pages_table = PagesTable(data=NdrCorePage.objects.all().order_by('index'))
        forms_table = SearchConfigurationTable(data=SearchConfiguration.objects.all())
        settings_table = SettingsTable(data=NdrCoreValue.objects.all())

        return render(self.request,
                      template_name='ndr_core/admin_views/dashboard.html',
                      context={'pages_table': pages_table,
                               'forms_table': forms_table,
                               'settings_table': settings_table})


class ManagePages(LoginRequiredMixin, View):
    """TODO """

    def get(self, request, *args, **kwargs):
        return render(self.request,
                      template_name='ndr_core/admin_views/configure_pages.html',
                      context=self.get_context_data())

    def get_context_data(self, **kwargs):
        pages_table = PagesManageTable(data=NdrCorePage.objects.all().order_by('index'))
        context = {'pages_table': pages_table}
        return context


class ConfigureSettings(LoginRequiredMixin, View):

    def get_settings_tables(self):
        basic_settings = ChangeSettingsTable(data=NdrCoreValue.objects.filter(value_name__in=['header_default_title',
                                                                                              'header_description',
                                                                                              'header_author']))

        contact_settings = ChangeSettingsTable(data=NdrCoreValue.objects.filter(value_name__in=['contact_form_default_subject',
                                                                                                'email_config_host',
                                                                                                'email_config_timeout',
                                                                                                'contact_form_send_to_address',
                                                                                                'contact_form_send_from_address']))
        return basic_settings, contact_settings

    def get(self, request, *args, **kwargs):
        basic_settings, contact_settings = self.get_settings_tables()

        return render(self.request,
                      template_name='ndr_core/admin_views/configure_settings.html',
                      context={'basic_settings_table': basic_settings,
                               'contact_settings_table': contact_settings})

    def post(self, request, *args, **kwargs):
        basic_settings, contact_settings = self.get_settings_tables()
        for key in request.POST.keys():
            value = request.POST.get(key)
            if key.startswith('save_'):
                key = key[5:]
                print(key)
                v_object = NdrCoreValue.objects.get(value_name=key)
                v_object.value_value = value
                v_object.save()

        messages.success(request, "Saved Changes")
        return render(self.request,
                      template_name='ndr_core/admin_views/configure_settings.html',
                      context={'basic_settings_table': basic_settings,
                               'contact_settings_table': contact_settings})


class ConfigureApi(LoginRequiredMixin, View):
    """TODO """

    def get(self, request, *args, **kwargs):
        return render(self.request, template_name='ndr_core/admin_views/configure_api.html',
                      context=self.get_context_data())

    def get_context_data(self, **kwargs):
        apis_table = ApiTable(data=ApiConfiguration.objects.all().order_by('api_name'))
        context = {'apis_table': apis_table}

        return context


class ConfigureSearch(LoginRequiredMixin, View):
    """TODO """

    def get(self, request, *args, **kwargs):
        return render(self.request, template_name='ndr_core/admin_views/configure_search.html',
                      context=self.get_context_data())

    def get_context_data(self, **kwargs):
        search_config_table = SearchConfigurationTable(data=SearchConfiguration.objects.all())
        context = {'search_config_table': search_config_table}

        return context


class PageCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new NdrCorePage """

    model = NdrCorePage
    form_class = PageForm
    success_url = reverse_lazy('ndr_core:configure_pages')
    template_name = 'ndr_core/admin_views/page_create.html'

    def form_valid(self, form):
        response = super(PageCreateView, self).form_valid(form)

        max_index = NdrCorePage.objects.aggregate(Max('index'))
        new_index = max_index["index__max"] + 1
        self.object.index = new_index
        self.object.save()

        # If the new page is a CONTACT page, don't add it
        if self.object.page_type == self.object.PageType.CONTACT:
            existing_contact_forms = NdrCorePage.objects.filter(page_type=self.object.PageType.CONTACT).count()
            if existing_contact_forms > 0:
                self.object.delete()
                messages.error(self.request, "You can only add one contact form")
                return response

        app_name = NdrSettings.APP_NAME
        new_filename = f'{app_name}/templates/{app_name}/{form.cleaned_data["view_name"]}.html'
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
    form_class = PageForm
    success_url = reverse_lazy('ndr_core:configure_pages')
    template_name = 'ndr_core/admin_views/page_edit.html'

    def form_valid(self, form):
        response = super(PageEditView, self).form_valid(form)
        return response


class PageDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete an NdrCorePage from the database. Asks to confirm.
    This function also deletes the created HTML template. """

    model = NdrCorePage
    success_url = reverse_lazy('ndr_core:configure_pages')
    template_name = 'ndr_core/admin_views/page_confirm_delete.html'

    def form_valid(self, form):
        filename = f'{NdrSettings.APP_NAME}/templates/{NdrSettings.APP_NAME}/{self.object.view_name}.html'
        if os.path.isfile(filename):
            os.remove(filename)
        else:
            messages.warning(self.request, "HTML template was not found.")

        return super(PageDeleteView, self).form_valid(form)


# API CONFIGURATION----------------------------------------------------------------------------------------------------
class ApiConfigurationCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new API configuration """

    model = ApiConfiguration
    form_class = ApiForm
    success_url = reverse_lazy('ndr_core:configure_api')
    template_name = 'ndr_core/admin_views/api_create.html'

    def form_valid(self, form):
        response = super(ApiConfigurationCreateView, self).form_valid(form)
        return response


class ApiConfigurationEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing API configuration """

    model = ApiConfiguration
    form_class = ApiForm
    success_url = reverse_lazy('ndr_core:configure_api')
    template_name = 'ndr_core/admin_views/api_edit.html'


class ApiConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete an API configuration from the database. Asks to confirm."""

    model = ApiConfiguration
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
        context["search_field_table"] = SearchFieldTable(data=NdrSearchField.objects.all())
        return context


class SearchFieldConfigurationCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new Search Field """

    model = NdrSearchField
    form_class = SearchFieldForm
    success_url = reverse_lazy('ndr_core:configure_search_fields')
    template_name = 'ndr_core/admin_views/search_field_create.html'

    def form_valid(self, form):
        response = super(SearchFieldConfigurationCreateView, self).form_valid(form)
        return response


class SearchFieldConfigurationEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing Search field """

    model = NdrSearchField
    form_class = SearchFieldForm
    success_url = reverse_lazy('ndr_core:configure_search_fields')
    template_name = 'ndr_core/admin_views/search_field_edit.html'


class SearchFieldConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    model = NdrSearchField
    success_url = reverse_lazy('ndr_core:configure_search_fields')
    template_name = 'ndr_core/admin_views/search_field_confirm_delete.html'

    def form_valid(self, form):
        return super(SearchFieldConfigurationDeleteView, self).form_valid(form)


@login_required
def create_search_fields(request, schema_pk):
    """ Creates a list of NdrSearchField objects based on a schema definition.
    Available search fields depend on the data one wants to access. They can be added manually but also depending
    on an existing data schema if it is known to ndr_core.

        :param request: The page's request object
        :param schema_pk: The primary key of the schema object to create search fields from
        :return: A redirect response to to 'configure_search_fields'
    """

    try:
        schema = NdrCoreDataSchema.objects.get(id=schema_pk)
        existing_fields = NdrSearchField.objects.filter(schema_name=schema.schema_name)
        if existing_fields.count() > 0:
            messages.warning(request, "Existing fields have been overwritten")
            existing_fields.delete()
        call_command('loaddata', schema.fixture_name, app_label='ndr_core')
        messages.success(request, "The Search fields were created")
        return redirect('ndr_core:configure_search_fields')
    except NdrCoreDataSchema.DoesNotExist:
        messages.error(request, "The Schema was not found in the database")
        return redirect('ndr_core:configure_search_fields')


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

    model = SearchConfiguration
    form_class = SearchConfigurationForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/search_config_create.html'

    def form_valid(self, form):
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
                new_field = SearchFieldFormConfiguration.objects.create(search_field=form.cleaned_data[f'search_field_{row}'],
                                                                        field_row=form.cleaned_data[f'row_field_{row}'],
                                                                        field_column=form.cleaned_data[f'column_field_{row}'],
                                                                        field_size=form.cleaned_data[f'size_field_{row}'])
                self.object.search_form_fields.add(new_field)

        return response


class SearchConfigurationEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing API configuration """

    model = SearchConfiguration
    form_class = SearchConfigurationForm
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/search_config_edit.html'


class SearchConfigurationDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete a Search Field from the database. Asks to confirm."""

    model = SearchConfiguration
    success_url = reverse_lazy('ndr_core:configure_search')
    template_name = 'ndr_core/admin_views/search_config_confirm_delete.html'

    def form_valid(self, form):
        return super(SearchConfigurationDeleteView, self).form_valid(form)


def preview_image(request, img_config):
    data = []
    config_rows = img_config.split(",")
    for row in config_rows:
        config_row = row.split("~")
        if '' not in config_row:
            data.append({
                'row': int(config_row[0]),
                'col': int(config_row[1]),
                'size': int(config_row[2]),
                'text': NdrSearchField.objects.get(id=int(config_row[3])).field_label})
    image_data = get_image_from_raw_data(data)
    return HttpResponse(image_data, content_type="image/png")