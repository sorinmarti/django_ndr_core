import json
import re

from django.contrib import messages
from django.contrib.staticfiles import finders
from django.http import HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy

from django.views import View
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import FormMixin, CreateView

from ndr_core.geo_ip_utils import get_user_ip, get_geolocation
from ndr_core.forms import FilterForm, ContactForm, AdvancedSearchForm, SimpleSearchForm, TestForm
from ndr_core.models import NdrCorePage, NdrCoreApiConfiguration, NdrCoreValue, NdrCoreSearchStatisticEntry,\
    NdrCoreUserMessage, NdrCoreImage, NdrCoreUIElement
from ndr_core.api_factory import ApiFactory
from ndr_core.ndr_settings import NdrSettings


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
            return SimpleSearchView.as_view(template_name=f'ndr/{page.view_name}.html',
                                            ndr_page=page)(request)
        elif page.page_type == page.PageType.SEARCH:
            return SearchView.as_view(template_name=f'ndr/{page.view_name}.html',
                                      ndr_page=page)(request)
        elif page.page_type == page.PageType.COMBINED_SEARCH:
            return SearchView.as_view(template_name=f'ndr/{page.view_name}.html',
                                      ndr_page=page)(request)
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
        context = {'page': self.ndr_page, 'navigation': NdrCorePage.objects.all().order_by('index'),
                   'my_data': {
                       'slides': NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.BGS),
                       'show_indicators': True,
                       'show_title': True,
                       'show_caption': True
                   }}
        return context


class NdrTemplateView(_NdrCoreView):
    """Basic template view. (Is currently the same as _NdrCoreView) """

    def get_ndr_context_data(self):
        context = super(NdrTemplateView, self).get_ndr_context_data()
        page_text = context['page'].template_text

        # Search for ui-elements to insert
        if page_text is not None and page_text != '':
            rendered_text = page_text
            match = re.search(r'(\[\[)(card|slideshow|carousel|jumbotron)\|([0-9]*)(\]\])', rendered_text)
            while match:
                template = match.groups()[1]
                element_id = match.groups()[2]
                try:
                    element = NdrCoreUIElement.objects.get(id=int(element_id))
                    element_html_string = render_to_string(f'ndr_core/ui_elements/{template}.html',
                                                           request=self.request, context={'data': element})


                    rendered_text = rendered_text.replace(f'[[{template}|{element_id}]]', element_html_string)
                    context['rendered_text'] = rendered_text
                except NdrCoreUIElement.DoesNotExist:
                    pass  # TODO

                match = re.search(r'(\[\[)(card|slideshow|carousel|jumbotron)\|([0-9]*)(\]\])', rendered_text)
        return context


class NdrTestView(_NdrCoreView):
    """Shows a test view to test the UI settings """

    def get(self, request, *args, **kwargs):
        form = TestForm()
        return render(request, f"{NdrSettings.APP_NAME}/test.html", {'form': form})


class NdrDownloadView(View):
    """Returns a json from an ID request to the API """

    def get(self, request, *args, **kwargs):
        try:
            api_config = NdrCoreApiConfiguration.objects.get(api_name=self.kwargs['api_config'])
            api_factory = ApiFactory(api_config)
            api = api_factory.get_query_class()(api_config)
            query = api.get_record_query(self.kwargs['record_id'])
            result = api_factory.get_result_class()(api_config, query, self.request)
            result.load_result(transform_result=False)
            return JsonResponse(result.raw_result)
        except NdrCoreApiConfiguration.DoesNotExist:
            return JsonResponse({})


class FilterListView(_NdrCoreView):
    """TODO """

    def get(self, request, *args, **kwargs):
        form = FilterForm()
        choices = list()
        search_metadata = {}

        context = self.get_ndr_context_data()
        context.update({'results': choices, 'form': form, 'meta': search_metadata})
        return render(request, self.template_name, context)


class SearchView(_NdrCoreView):
    """TODO """

    def get(self, request, *args, **kwargs):
        requested_search = None
        form = AdvancedSearchForm(ndr_page=self.ndr_page)

        if request.method == "GET":
            # Check if/which a search button has been pressed
            for value in request.GET.keys():
                if value.startswith('search_button_'):
                    requested_search = value[len('search_button_'):]
                    break

            # If a button has been pressed: reinitialize form with values and check its validity
            if requested_search is not None:
                form = AdvancedSearchForm(request.GET, ndr_page=self.ndr_page)
                # If the form is valid: create a search query
                if form.is_valid():
                    statistics_enabled = NdrCoreValue.get_or_initialize("statistics_feature", init_value="false").value_value == "true"
                    statistics_api = None

                    if requested_search == 'simple':
                        statistics_api = self.ndr_page.simple_api
                        api_factory = ApiFactory(self.ndr_page.simple_api)
                        query = api_factory.get_query_class()(self.ndr_page.simple_api, page=request.GET.get("page", 1))
                        search_term = request.GET.get('search_term', '')
                        query_string = query.get_simple_query(search_term)
                    else:
                        search_config = self.ndr_page.search_configs.get(conf_name=requested_search)
                        statistics_api = search_config.api_configuration
                        api_factory = ApiFactory(search_config.api_configuration)
                        query = api_factory.get_query_class()(search_config.api_configuration, page=request.GET.get("page", 1))
                        search_term = ''
                        for key in request.GET.keys():
                            if search_config.search_form_fields.filter(search_field__field_name=key).count() > 0:
                                query.set_value(key, request.GET.get(key))
                                search_term += f"{key}={request.GET.get(key)}, "
                        query_string = query.get_advanced_query()

                    if statistics_enabled:
                        ip = get_user_ip(request)
                        location = get_geolocation(ip)
                        NdrCoreSearchStatisticEntry.objects.create(search_api=statistics_api,
                                                                   search_term=search_term,
                                                                   search_location=location)

                    print(query_string)
            else:
                print("No search")

        context = self.get_ndr_context_data()
        context.update({'form': form, 'requested_search': requested_search})
        return render(request, self.template_name, context)


class SimpleSearchView(_NdrCoreView):
    """TODO """

    def get(self, request, *args, **kwargs):
        form = SimpleSearchForm(ndr_page=self.ndr_page)
        context = self.get_ndr_context_data()

        if request.method == "GET":
            form = SimpleSearchForm(request.GET, ndr_page=self.ndr_page)

            if "search_button_simple" in request.GET.keys():
                api_factory = ApiFactory(self.ndr_page.simple_api)
                query = api_factory.get_query_class()(self.ndr_page.simple_api)
                query_string = query.get_simple_query(request.GET.get('search_term', ''), request.GET.get("page", 1))
                result = api_factory.get_result_class()(self.ndr_page.simple_api, query_string, self.request)
                result.load_result()
                context.update({'api_config': self.ndr_page.simple_api})
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
        pass


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
