"""This file contains the main NDR Core views. For the views for the administration interface, see admin_views/* """
import json

from django.contrib import messages
from django.contrib.staticfiles import finders
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.urls import reverse

from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from django_ndr_core import settings
from ndr_core.forms import FilterForm, ContactForm, AdvancedSearchForm, SimpleSearchForm, TestForm, \
    ManifestSelectionForm
from ndr_core.map_test import get_map
from ndr_core.models import (
    NdrCorePage,
    NdrCoreUserMessage,
    NdrCoreImage,
    NdrCoreCorrection,
    NdrCoreSearchConfiguration,
    NdrCoreValue,
    NdrCoreManifest,
)
from ndr_core.api_factory import ApiFactory
from ndr_core.ndr_settings import NdrSettings
from ndr_core.templatetags.ndr_utils import url_deparse
from ndr_core.ndr_template_tags import TextPreRenderer
from ndr_core.utils import create_csv_export_string


def dispatch(request, ndr_page=None):
    """All requests for ndr_core pages are routed through this function which decides the
    type of page which should be returned based on the configuration. If the ndr_page is None,
    the index page is returned.

    :param request: The page's request object
    :param ndr_page: The NdrCorePage's database id
    :return: A configured view or 404 if not found
    """

    page_is_under_construction = NdrCoreValue.get_or_initialize("under_construction",
                                                                init_type=NdrCoreValue.ValueType.BOOLEAN,
                                                                init_value="false").get_value()

    if page_is_under_construction:
        return TemplateView.as_view(template_name='ndr_core/under_construction.html')(request)

    if ndr_page is None:
        ndr_page = 'index'

    try:
        page = NdrCorePage.objects.get(view_name=ndr_page)

        if page.page_type == page.PageType.TEMPLATE:
            return NdrTemplateView.as_view(template_name=f'{NdrSettings.APP_NAME}/{page.view_name}.html',
                                           ndr_page=page)(request)
        elif page.page_type == page.PageType.FILTER_LIST:
            return FilterListView.as_view(template_name=f'{NdrSettings.APP_NAME}/{page.view_name}.html',
                                          ndr_page=page)(request)
        elif page.page_type == page.PageType.SIMPLE_SEARCH:
            return SearchView.as_view(template_name=f'{NdrSettings.APP_NAME}/{page.view_name}.html',
                                      ndr_page=page,
                                      form_class=SimpleSearchForm)(request)
        elif page.page_type == page.PageType.SEARCH:
            return SearchView.as_view(template_name=f'{NdrSettings.APP_NAME}/{page.view_name}.html',
                                      ndr_page=page,
                                      form_class=AdvancedSearchForm)(request)
        elif page.page_type == page.PageType.COMBINED_SEARCH:
            return SearchView.as_view(template_name=f'{NdrSettings.APP_NAME}/{page.view_name}.html',
                                      ndr_page=page,
                                      form_class=AdvancedSearchForm)(request)
        elif page.page_type == page.PageType.CONTACT:
            return ContactView.as_view(template_name=f'{NdrSettings.APP_NAME}/{page.view_name}.html',
                                       ndr_page=page)(request)
        elif page.page_type == page.PageType.FLIP_BOOK:
            return FlipBookView.as_view(template_name=f'{NdrSettings.APP_NAME}/{page.view_name}.html',
                                        ndr_page=page)(request)
        elif page.page_type == page.PageType.ABOUT_PAGE:
            return AboutUsView.as_view(template_name=f'{NdrSettings.APP_NAME}/{page.view_name}.html',
                                       ndr_page=page)(request)
        elif page.page_type == page.PageType.VIEWER_PAGE:
            return ViewerView.as_view(template_name=f'{NdrSettings.APP_NAME}/{page.view_name}.html',
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
        """ Default get method for all ndr core pages. """
        return render(request, self.template_name, self.get_ndr_context_data())

    def get_ndr_context_data(self):
        """ Returns the page object, the pre-rendered page text, the navigation items and the partner image objects. """
        context = {'page': self.ndr_page,
                   'rendered_text': self.pre_render_text(),
                   'navigation': NdrCorePage.objects.filter(parent_page=None).order_by('index'),
                   'partners': NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.LOGOS)}
        return context

    def pre_render_text(self):
        """ An NDR Core page can have a page text with certain [[style|tags]]. They are replaced by the respective
         HTML element by the TextPreRenderer. """

        page_text = self.ndr_page.translated_template_text()
        if page_text is None or page_text == '':
            return ''

        pre_renderer = TextPreRenderer(page_text, self.request)
        rendered_page_text = pre_renderer.get_pre_rendered_text()
        return rendered_page_text


class NdrTemplateView(_NdrCoreView):
    """Basic template view. """
    pass


class NdrTestView(_NdrCoreView):
    """ Shows a test view to test the UI settings. Features a form to test form rendering.
     Users can change colors and style of their pages. With this test page they can see how
     all the elements look. """

    def get(self, request, *args, **kwargs):
        form = TestForm()
        return render(request, f"{NdrSettings.APP_NAME}/test.html", {'form': form})


class _NdrCoreSearchView(_NdrCoreView):
    """ Base View for all NDR Core search views. A search view in this context means all views used to
     retrieve or display results. It is also the base view for all result download views."""

    form_class = AdvancedSearchForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_simple_search_mockup_config(self):
        """All search related functions expect a SearchConfiguration but the simple search only provides an
        ApiConfiguration. This returns a mockup config with the simple-search-api-configuration."""
        return NdrCoreSearchConfiguration.get_simple_search_mockup_config(self.ndr_page.simple_api)

    @staticmethod
    def get_search_config_from_name(name):
        """ Convenience method to get search config. """
        try:
            return NdrCoreSearchConfiguration.objects.get(conf_name=name)
        except NdrCoreSearchConfiguration.DoesNotExist:
            return None

    def fill_search_query_values(self, requested_search, query_obj):
        """ Translates the GET parameters provided by the search form to key-value pairs
        and saves them in the Query-object. """
        search_config = self.get_search_config_from_name(requested_search)
        form = self.form_class(self.request.GET, search_config=search_config)
        form.is_valid()

        for field in form.fields:
            if field.startswith(requested_search):
                # This removes the search conf name, leaving the actual field name
                actual_key = field[len(requested_search) + 1:]
                if search_config.search_form_fields.filter(search_field__field_name=actual_key).count() > 0:
                    query_obj.set_value(actual_key, form.cleaned_data[field])

        """for key in self.request.GET.keys():
            if key.startswith(requested_search):
                actual_key = key[len(requested_search) + 1:]
                if search_config.search_form_fields.filter(search_field__field_name=actual_key).count() > 0:
                    query_obj.set_value(actual_key, form.cleaned_data[key])"""


class NdrDownloadView(_NdrCoreSearchView):
    """Returns a JSON record from an ID request to the API """

    def get(self, request, *args, **kwargs):
        api_factory = ApiFactory(self.get_search_config_from_name(self.kwargs['search_config']))
        api = api_factory.get_query_instance()
        record_id = url_deparse(self.kwargs['record_id'])
        query = api.get_record_query(record_id)
        result = api_factory.get_result_instance(query, self.request)
        result.load_result(transform_result=False)
        return JsonResponse(result.raw_result)  # TODO RFQ: Is raw_result the right one?


class NdrListDownloadView(_NdrCoreSearchView):
    """Returns a JSON record list from a search result. """

    def __init__(self):
        super().__init__()
        self.page_size = None

    def create_result_for_response(self):
        search_config = self.get_search_config_from_name(self.kwargs['search_config'])
        api_factory = ApiFactory(search_config)

        query_obj = api_factory.get_query_instance(page=self.request.GET.get("page", 1))
        self.fill_search_query_values(self.kwargs['search_config'], query_obj)
        query_string = query_obj.get_advanced_query()
        result = api_factory.get_result_instance(query_string, self.request)
        result.page_size = NdrCoreValue.get_or_initialize("search_download_max_results",
                                                          init_type=NdrCoreValue.ValueType.INTEGER,
                                                          init_value="250").get_value()
        result.load_result(transform_result=False)
        return result

    def get(self, request, *args, **kwargs):
        result = self.create_result_for_response()
        return JsonResponse(result.raw_result)   # TODO RFQ: Is raw_result the right one?


class NdrCSVListDownloadView(NdrListDownloadView):
    def get(self, request, *args, **kwargs):
        search_config = self.get_search_config_from_name(self.kwargs['search_config'])

        result = self.create_result_for_response()
        mapping = [
            {"field": search_config.api_configuration.api_id_field, "header": "ID"},
        ]
        search_config = self.get_search_config_from_name(self.kwargs['search_config'])
        for field in search_config.search_form_fields.all():
            if field.search_field.use_in_csv_export:
                mapping.append({"field": field.search_field.api_parameter, "header": field.search_field.field_label})

        csv_string = create_csv_export_string(result.raw_result['hits'], mapping)
        return HttpResponse(csv_string, content_type="text/csv")


class NdrMarkForCorrectionView(View):
    def get(self, request, *args, **kwargs):
        search_config = NdrCoreSearchConfiguration.objects.get(conf_name=self.kwargs['search_config'])
        NdrCoreCorrection.objects.create(corrected_dataset=search_config,
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
        form = self.form_class(ndr_page=self.ndr_page)

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
                    search_term = request.GET.get('search_term', '')
                    if search_term == '':
                        messages.error(request, _('Please enter a search term.'))
                        context.update({'form': form, 'requested_search': requested_search})
                        return render(request, self.template_name, context)

                    search_config = self.get_simple_search_mockup_config()
                    api_factory = ApiFactory(search_config)
                    query_obj = api_factory.get_query_instance(page=request.GET.get("page", 1))
                    query_string = query_obj.get_simple_query(request.GET.get('search_term', ''),
                                                              request.GET.get("page", 1),
                                                              and_or=request.GET.get('and_or_field', 'and'))
                else:
                    has_values = False
                    for field in form.fields:
                        if field.startswith(requested_search):
                            if form.cleaned_data[field] not in [None, '', []]:
                                has_values = True
                                break

                    if not has_values:
                        messages.error(request, _('Please fill out at least one search field.'))
                        context.update({'form': form, 'requested_search': requested_search})
                        return render(request, self.template_name, context)

                    search_config = self.ndr_page.search_configs.get(conf_name=requested_search)
                    api_factory = ApiFactory(search_config)
                    query_obj = api_factory.get_query_instance(page=request.GET.get("page", 1))
                    self.fill_search_query_values(requested_search, query_obj)
                    query_string = query_obj.get_advanced_query()

                # Create a result object and load the result
                result = api_factory.get_result_instance(query_string, self.request)
                result.load_result()

                if result.total == 0:
                    messages.error(request, _('No results found.'))
                else:
                    context.update({'api_config': search_config.api_configuration})
                    for r in result.results:
                        origin = r['data']['port_of_origin']['scheme']
                        destination = r['data']['port_of_destination']['scheme']
                        amap = get_map([
                            [origin['identifier'], origin['name'], origin['lat'], origin['lng']],
                            [destination['identifier'], destination['name'], destination['lat'], destination['lng']]
                        ])
                        r['map'] = amap

                    context.update({'result': result})
        else:
            if "refine" in request.GET.keys():
                form = self.form_class(request.GET, ndr_page=self.ndr_page)

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
                query_string = query.get_simple_query(request.GET.get('search_term', ''),
                                                      request.GET.get("page", 1),
                                                      and_or=request.GET.get('and_or_field', 'and'))
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
        answer = super().form_valid(form)
        messages.success(self.request, _("Thank you! The message has been sent."))

        # A message object is created and saved. Now the message should be sent to a forwarding address.
        # If it is sc configured.
        # TODO SEND EMAIL

        return answer

    def form_invalid(self, form):
        messages.error(self.request, _("Please correct the errors below."))
        return super().form_invalid(form)


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


class ViewerView(_NdrCoreView):
    """A view to show a IIIF viewer. """
    def get_context_data(self, **kwargs):
        context = {}
        context.update(self.get_ndr_context_data())
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        manifests = NdrCoreManifest.objects.all()

        form = None
        manifest_url = None

        if manifests.count() == 0:
            messages.error(request, _("No manifests found."))
        elif manifests.count() == 1:
            manifest_url = manifests[0].file.url
        else:
            form = ManifestSelectionForm(request.GET)
            if form.is_valid():
                manifest_url = form.cleaned_data['manifest'].file.url
            else:
                form = ManifestSelectionForm(initial={'manifest': manifests[0].id})
                manifest_url = manifests[0].file.url

        context['form'] = form
        context['manifest_url'] = manifest_url
        context['page_to_display'] = request.GET.get('page', 1)

        return render(request, self.template_name, context)


def set_language_view(request, new_language):
    """A view to set the language of the page. """
    print(f"SET TO {new_language}")
    translation.activate(new_language)

    redirect_url = request.META.get('HTTP_REFERER')
    if redirect_url is None:
        redirect_url = reverse(f'{NdrSettings.APP_NAME}:index')

    response = HttpResponseRedirect(redirect_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, new_language)

    return response
