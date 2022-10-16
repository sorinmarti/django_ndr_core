from django.http import HttpResponseNotFound
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.generic import TemplateView

from ndr_core.forms import FilterForm, ContactForm, AdvancedSearchForm, SimpleSearchForm
from ndr_core.models import NdrCorePage
from ndr_core.query import Query


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
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {'page': self.ndr_page}
        return context


class NdrTemplateView(_NdrCoreView):
    pass


class FilterListView(_NdrCoreView):

    def get(self, request, *args, **kwargs):
        form = FilterForm()
        choices = list()
        search_metadata = {}

        context = self.get_context_data()
        context.update({'results': choices, 'form': form, 'meta': search_metadata})
        return render(request, self.template_name, context)


class SearchView(_NdrCoreView):

    def get(self, request, *args, **kwargs):
        form = AdvancedSearchForm(ndr_page=self.ndr_page)
        if request.method == "GET":
            # Check if/which a search button has been pressed
            requested_search = None
            for value in request.GET.keys():
                if value.startswith('search_button_'):
                    requested_search = value[len('search_button_'):]
                    break

            # If a button has been pressed: reinitialize form with values and check its validity
            if requested_search is not None:
                form = AdvancedSearchForm(request.GET, ndr_page=self.ndr_page)
                if form.is_valid():
                    if requested_search == 'simple':
                        query = Query(self.ndr_page.simple_api)
                        query_string = query.get_simple_query(request.GET.get('search_term', ''), request.GET.get("page", 1))
                    else:
                        search_config = self.ndr_page.search_configs.get(conf_name=requested_search)
                        query = Query(search_config.api_configuration)
                        for key in request.GET.keys():
                            if search_config.search_form_fields.filter(search_field__field_name=key).count() > 0:
                                query.set_value(key, request.GET.get(key))
                        query_string = query.get_advanced_query(request.GET.get("page", 1))
                    print(query_string)
            else:
                print("No search")

        context = self.get_context_data()
        context.update({'form': form, 'requested_search': requested_search})
        return render(request, self.template_name, context)


class SimpleSearchView(_NdrCoreView):

    def get(self, request, *args, **kwargs):
        form = SimpleSearchForm(ndr_page=self.ndr_page)
        if request.method == "GET":
            form = SimpleSearchForm(request.GET, ndr_page=self.ndr_page)
            """if form.is_valid():
                query = Query(self.search_config.api_configuration)
                for key in request.GET.keys():
                    if self.search_config.search_form_fields.filter(search_field__field_name=key).count() > 0:
                        query.set_value(key, request.GET.get(key))
                query_string = query.get_advanced_query(request.GET.get("page", 1))
                print(query_string)"""

        context = self.get_context_data()
        context.update({'form': form})
        return render(request, self.template_name, context)


class ContactView(_NdrCoreView):

    def get(self, request, *args, **kwargs):
        form = ContactForm()

        if request.method == "GET":
            if form.is_valid():
                pass

        context = self.get_context_data()
        context.update({'form': form})
        return render(request, self.template_name, context)
