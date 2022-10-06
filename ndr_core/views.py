from django.http import HttpResponseNotFound
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.generic import TemplateView

from ndr_core.forms import FilterForm, ContactForm
from ndr_core.models import NdrCorePage


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
            return TemplateView.as_view(template_name=f'ndr/{page.view_name}.html')(request)
        elif page.page_type == page.PageType.FILTER_LIST:
            return FilterListView.as_view(template_name=f'ndr/{page.view_name}.html')(request)
        elif page.page_type == page.PageType.SIMPLE_SEARCH:
            return SearchView.as_view(template_name=f'ndr/{page.view_name}.html')(request)
        elif page.page_type == page.PageType.SEARCH:
            return SearchView.as_view(template_name=f'ndr/{page.view_name}.html')(request)
        elif page.page_type == page.PageType.COMBINED_SEARCH:
            return SearchView.as_view(template_name=f'ndr/{page.view_name}.html')(request)
        elif page.page_type == page.PageType.CONTACT:
            return ContactView.as_view(template_name=f'ndr/{page.view_name}.html')(request)
        else:
            return HttpResponseNotFound("Page Type Not Found")
    except NdrCorePage.DoesNotExist:
        return TemplateView.as_view(template_name='ndr_core/not_found.html')(request)


class _NdrCoreView(View):
    """ Base view for all configured ndr_core views. """

    template_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FilterListView(_NdrCoreView):

    def get(self, request, *args, **kwargs):
        form = FilterForm()
        choices = list()
        search_metadata = {}

        return render(request, self.template_name, {'results': choices, 'form': form, 'meta': search_metadata})


class SearchView(_NdrCoreView):
    pass


class ContactView(_NdrCoreView):

    def get(self, request, *args, **kwargs):
        form = ContactForm()

        return render(request, self.template_name, {'form': form})
