import json
import re
import pandas as pd

from django.contrib import messages
from django.contrib.staticfiles import finders
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from ndr_core.forms import FilterForm, ContactForm, AdvancedSearchForm, SimpleSearchForm, TestForm
from ndr_core.models import NdrCorePage, NdrCoreApiConfiguration, NdrCoreUserMessage, NdrCoreImage, NdrCoreUIElement, \
    NdrCoreUpload, NdrCoreCorrection, NdrCoreSearchConfiguration
from ndr_core.api_factory import ApiFactory
from ndr_core.ndr_settings import NdrSettings
from ndr_core.templatetags.ndr_utils import url_deparse


def dispatch(request, ndr_page):
    """All requests for ndr_core pages are routed through this function which decides the
    type of page which should be returned based on the configuration

    :param request: The page's request object
    :param ndr_page: The NdrCorePage's database id
    :return: A configured view or 404 if not found
    """
    try:
        page = NdrCorePage.objects.get(view_name=ndr_page)

        if page.page_type == page.PageType.TEMPLATE:
            return NdrTemplateView.as_view(template_name=f'ndr/{page.view_name}.html',
                                           ndr_page=page)(request)
        elif page.page_type == page.PageType.FILTER_LIST:
            return FilterListView.as_view(template_name=f'ndr/{page.view_name}.html',
                                          ndr_page=page)(request)
        elif page.page_type == page.PageType.SIMPLE_SEARCH:
            return SearchView.as_view(template_name=f'ndr/{page.view_name}.html',
                                      ndr_page=page,
                                      form_class=SimpleSearchForm)(request)
        elif page.page_type == page.PageType.SEARCH:
            return SearchView.as_view(template_name=f'ndr/{page.view_name}.html',
                                      ndr_page=page,
                                      form_class=AdvancedSearchForm)(request)
        elif page.page_type == page.PageType.COMBINED_SEARCH:
            return SearchView.as_view(template_name=f'ndr/{page.view_name}.html',
                                      ndr_page=page,
                                      form_class=AdvancedSearchForm)(request)
        elif page.page_type == page.PageType.CONTACT:
            return ContactView.as_view(template_name=f'ndr/{page.view_name}.html',
                                       ndr_page=page)(request)
        elif page.page_type == page.PageType.FLIP_BOOK:
            return FlipBookView.as_view(template_name=f'ndr/{page.view_name}.html',
                                        ndr_page=page)(request)
        elif page.page_type == page.PageType.ABOUT_PAGE:
            return AboutUsView.as_view(template_name=f'ndr/{page.view_name}.html',
                                       ndr_page=page)(request)
        else:
            return HttpResponseNotFound("Page Type Not Found")
    except NdrCorePage.DoesNotExist:
        return TemplateView.as_view(template_name='ndr_core/not_found.html')(request)


class _NdrCoreView(View):
    """ Base view for all configured ndr_core views. """

    ndr_page = None
    template_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_ndr_context_data())

    def get_ndr_context_data(self):
        context = {'page': self.ndr_page, 'navigation': NdrCorePage.objects.filter(parent_page=None).order_by('index'),
                   'partners': NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.LOGOS)
                   }
        return context


class NdrTemplateView(_NdrCoreView):
    """Basic template view. (Is currently the same as _NdrCoreView) """

    ui_element_regex = r'(\[\[)(card|slideshow|carousel|jumbotron|figure|banner|file|page)\|([0-9]*)(\]\])'

    def get_ndr_context_data(self):
        context = super(NdrTemplateView, self).get_ndr_context_data()
        page_text = context['page'].template_text

        # Search for ui-elements to insert
        if page_text is not None and page_text != '':
            rendered_text = page_text
            match = re.search(self.ui_element_regex, rendered_text)
            while match:
                template = match.groups()[1]
                element_id = match.groups()[2]
                try:
                    if template == 'figure':
                        element = NdrCoreImage.objects.get(id=int(element_id))
                    elif template == 'file':
                        element = NdrCoreUpload.objects.get(id=int(element_id))
                    elif template == 'page':
                        element = NdrCorePage.objects.get(id=int(element_id))
                    else:
                        element = NdrCoreUIElement.objects.get(id=int(element_id))

                    element_html_string = render_to_string(f'ndr_core/ui_elements/{template}.html',
                                                           request=self.request, context={'data': element})

                    rendered_text = rendered_text.replace(f'[[{template}|{element_id}]]', element_html_string)

                except NdrCoreUIElement.DoesNotExist:
                    rendered_text = rendered_text.replace(f'[[{template}|{element_id}]]', "ERROR loading UI element")

                match = re.search(self.ui_element_regex, rendered_text)
            context['rendered_text'] = rendered_text
        else:
            context['rendered_text'] = ''
            
        return context


class NdrTestView(_NdrCoreView):
    """Shows a test view to test the UI settings """

    def get(self, request, *args, **kwargs):
        form = TestForm()
        return render(request, f"{NdrSettings.APP_NAME}/test.html", {'form': form})


class _NdrCoreSearchView(_NdrCoreView):
    """ View for all configured ndr_core search views. """

    form_class = AdvancedSearchForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_simple_search_mockup_config(self):
        search_config = NdrCoreSearchConfiguration()
        search_config.api_configuration = self.ndr_page.simple_api
        search_config.conf_name = 'simple'
        return search_config

    def get_search_config_from_name(self, name):
        return NdrCoreSearchConfiguration.objects.get(conf_name=name)

    def fill_search_query_values(self, requested_search, query_obj):
        search_config = self.get_search_config_from_name(requested_search)
        form = self.form_class(self.request.GET, search_config=search_config)
        form.is_valid()

        for key in self.request.GET.keys():
            if key.startswith(requested_search):
                actual_key = key[len(requested_search) + 1:]
                if search_config.search_form_fields.filter(search_field__field_name=actual_key).count() > 0:
                    query_obj.set_value(actual_key, form.cleaned_data[key])


class NdrDownloadView(_NdrCoreSearchView):
    """Returns a json from an ID request to the API """

    def get(self, request, *args, **kwargs):
        try:
            api_factory = ApiFactory(self.get_search_config_from_name(self.kwargs['search_config']))
            api = api_factory.get_query_instance()
            record_id = url_deparse(self.kwargs['record_id'])
            query = api.get_record_query(record_id)
            result = api_factory.get_result_instance(query, self.request)
            result.load_result(transform_result=False)
            return JsonResponse(result.raw_result)
        except NdrCoreApiConfiguration.DoesNotExist:
            return JsonResponse({})


class NdrListDownloadView(_NdrCoreSearchView):
    """Returns a json list from a search result. """

    def create_result_for_response(self):
        api_factory = ApiFactory(self.get_search_config_from_name(self.kwargs['search_config']))
        query_obj = api_factory.get_query_instance(page=self.request.GET.get("page", 1))
        self.fill_search_query_values(self.kwargs['search_config'], query_obj)
        query_string = query_obj.get_advanced_query()
        result = api_factory.get_result_instance(query_string, self.request)
        result.page_size = 250
        result.load_result(transform_result=False)
        return result

    def get(self, request, *args, **kwargs):
        try:
            result = self.create_result_for_response()
            return JsonResponse(result.raw_result)
        except NdrCoreApiConfiguration.DoesNotExist:
            return JsonResponse({})


class NdrCSVListDownloadView(NdrListDownloadView):
    def get(self, request, *args, **kwargs):
        try:
            result = self.create_result_for_response()
            json_string = json.dumps(result.raw_result['hits'])
            df = pd.read_json(json_string)
            csv_string = df.to_csv(encoding='utf-8')

            return HttpResponse(csv_string, content_type="text/csv")
        except NdrCoreApiConfiguration.DoesNotExist:
            return HttpResponse("")


class NdrMarkForCorrectionView(View):
    def get(self, request, *args, **kwargs):
        api_config = NdrCoreApiConfiguration.objects.get(api_name=self.kwargs['api_config'])
        NdrCoreCorrection.objects.create(corrected_dataset=api_config,
                                         corrected_record_id=url_deparse(self.kwargs['record_id']))
        return HttpResponse("OK")


class FilterListView(_NdrCoreView):
    """TODO This function is not implemented yet."""

    def get(self, request, *args, **kwargs):
        form = FilterForm()
        choices = list()
        search_metadata = {}

        context = self.get_ndr_context_data()
        context.update({'results': choices, 'form': form, 'meta': search_metadata})
        return render(request, self.template_name, context)


class SearchView(_NdrCoreSearchView):
    """A view to search for records in the configured API. """

    def get(self, request, *args, **kwargs):
        requested_search = None
        context = self.get_ndr_context_data()
        form = self.form_class(request.GET, ndr_page=self.ndr_page)

        # Check if/which a search button has been pressed
        for value in request.GET.keys():
            if value.startswith('search_button_'):
                requested_search = value[len('search_button_'):]
                break

        # If a button has been pressed: reinitialize form with values and check its validity
        if requested_search is not None:
            form = self.form_class(request.GET, ndr_page=self.ndr_page)
            # If the form is valid: create a search query
            if form.is_valid():
                # The search is either a simple or a custom/advanced search
                if requested_search == 'simple':
                    search_config = self.get_simple_search_mockup_config()
                    api_factory = ApiFactory(search_config)
                    query_obj = api_factory.get_query_instance(page=request.GET.get("page", 1))
                    query_string = query_obj.get_simple_query(request.GET.get('search_term', ''))
                else:
                    search_config = self.ndr_page.search_configs.get(conf_name=requested_search)
                    api_factory = ApiFactory(search_config)
                    query_obj = api_factory.get_query_instance(page=request.GET.get("page", 1))
                    self.fill_search_query_values(requested_search, query_obj)
                    query_string = query_obj.get_advanced_query()

                # Create a result object and load the result
                result = api_factory.get_result_instance(query_string, self.request)
                result.load_result()

                context.update({'api_config': search_config.api_configuration})
                context.update({'result': result})
        else:
            # If no button has been pressed
            pass

        context.update({'form': form, 'requested_search': requested_search})
        return render(request, self.template_name, context)


class SimpleSearchView(_NdrCoreSearchView):
    """TODO """

    def get(self, request, *args, **kwargs):
        form = SimpleSearchForm(ndr_page=self.ndr_page)
        context = self.get_ndr_context_data()

        if request.method == "GET":
            form = SimpleSearchForm(request.GET, ndr_page=self.ndr_page)

            if "search_button_simple" in request.GET.keys():
                search_config = self.get_simple_search_mockup_config()
                api_factory = ApiFactory(search_config)
                query = api_factory.get_query_instance()
                query_string = query.get_simple_query(request.GET.get('search_term', ''), request.GET.get("page", 1))
                result = api_factory.get_result_instance(query_string, self.request)
                result.load_result()
                context.update({'api_config': search_config.api_configuration})
                context.update({'result': result})

        context.update({'form': form})
        return render(request, self.template_name, context)


class ContactView(CreateView, _NdrCoreView):
    """A view to show a contact form """

    model = NdrCoreUserMessage
    form_class = ContactForm
    success_url = reverse_lazy('ndr:ndr_view', kwargs={'ndr_page': 'contact'})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_ndr_context_data())
        return context

    def form_valid(self, form):
        # TODO SEND EMAIL AND/OR CREATE USER MESSAGE OBJECT

        print("Send Email?")
        messages.success(self.request, "Thank you! The message has been sent.")
        return super().form_valid(form)


class AboutUsView(_NdrCoreView):
    """A view to show an about us page. """

    def get_context_data(self, **kwargs):
        context = {}
        context.update(self.get_ndr_context_data())
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        team_members = NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.PEOPLE)
        context['data'] = {'team_members': team_members}

        return render(request, self.template_name, context)


class FlipBookView(_NdrCoreView):
    """A view to show a set of pages with 'back' and 'forward' buttons. """

    def get_context_data(self, **kwargs):
        context = {}
        context.update(self.get_ndr_context_data())
        return context


class ApiTestView(View):
    """TODO """

    def get(self, request, *args, **kwargs):
        api_request = self.kwargs['api_request']
        json_response = {}

        if api_request == 'basic':
            json_response = json.load(open(finders.find('ndr_core/test_server_assets/test.json')))
        elif api_request == 'advanced':
            json_response = {}
        elif api_request == 'fulldata':
            json_response = json.load(open(finders.find('ndr_core/test_server_assets/test.json')))["hits"][0]
        elif api_request == 'list':
            json_response = {}

        return JsonResponse(json_response)


class NdrFileView(View):
    """TODO """

    file = None
    content_type = 'text/plain'

    def get(self, request, *args, **kwargs):

        if self.file is None:
            return JsonResponse({})
        else:
            filename = f"{NdrSettings.get_files_path()}/{self.file}"
            try:
                with open(filename, 'r') as file:
                    string = file.readlines()
                    return HttpResponse(string, content_type=self.content_type)
            except FileNotFoundError:
                return JsonResponse({"error": "file not found"})