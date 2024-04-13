"""This file contains the main NDR Core views. All Page views are defined here.
For the views for the administration interface, see admin_views/* """
import os

from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.urls import reverse

from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from django.conf import settings

from ndr_core.exceptions import NdrCorePageNotFound, PreRenderError
from ndr_core.forms.forms_contact import ContactForm
from ndr_core.forms.forms_search import AdvancedSearchForm

from ndr_core.models import (
    NdrCorePage,
    NdrCoreUserMessage,
    NdrCoreImage,
    NdrCoreCorrection,
    NdrCoreSearchConfiguration,
    NdrCoreValue,
    NdrCoreManifest,
    NdrCoreSearchField
)
from ndr_core.api_factory import ApiFactory
from ndr_core.ndr_settings import NdrSettings
from ndr_core.templatetags.ndr_utils import url_deparse
from ndr_core.ndr_template_tags import TextPreRenderer
from ndr_core.utils import create_csv_export_string


def get_page_type_view_class(page_type):
    """Returns the view class for a given page type. """
    translator = {
        NdrCorePage.PageType.TEMPLATE: NdrTemplateView,
        NdrCorePage.PageType.SEARCH: SearchView,
        NdrCorePage.PageType.CONTACT: ContactView,
        NdrCorePage.PageType.FLIP_BOOK: FlipBookView,
        NdrCorePage.PageType.ABOUT_PAGE: AboutUsView,
    }

    if page_type not in translator.keys():
        raise NdrCorePageNotFound(f"Page type {page_type} not found.")

    return translator[page_type]


def dispatch(request, ndr_page=None):
    """All requests for ndr_core pages are routed through this function which decides the
    type of page which should be returned based on the configuration. If the ndr_page is None,
    the index page is returned.

    :param request: The page's request object
    :param ndr_page: The NdrCorePage's database id
    :return: A configured view or 404 if not found
    """

    if request.path == reverse_lazy(f'{NdrSettings.APP_NAME}:robots'):
        return create_robots_txt_view(request)
    if request.path == reverse_lazy(f'{NdrSettings.APP_NAME}:sitemap'):
        return create_sitemap_view(request)

    page_is_under_construction = NdrCoreValue.get_or_initialize("under_construction",
                                                                init_type=NdrCoreValue.ValueType.BOOLEAN,
                                                                init_value="false").get_value()

    if page_is_under_construction:
        return TemplateView.as_view(template_name='ndr_core/under_construction.html')(request)

    if ndr_page is None:
        ndr_page = 'index'

    try:
        page = NdrCorePage.objects.get(view_name=ndr_page)
        view_class = get_page_type_view_class(page.page_type)

        return view_class.as_view(template_name=f'{NdrSettings.APP_NAME}/{page.view_name}.html',
                                  ndr_page=page)(request)
    except NdrCorePage.DoesNotExist:
        return TemplateView.as_view(template_name='ndr_core/404.html')(request, status=404)


def display_schema_or_404(request, schema_name):
    """Displays a schema or 404."""

    # Find the schema in the media files
    # If it exists, display it, otherwise display a 404

    schema_path = NdrSettings.get_schema_path()
    if schema_name in os.listdir(schema_path):
        with open(f'{schema_path}/{schema_name}', 'r') as schema_file:
            schema = schema_file.read()
            return HttpResponse(schema, content_type='text/plain')

    return render(request, 'ndr_core/404.html', status=404)


class _NdrCoreView(View):
    """ Base view for all configured ndr_core views. """

    ndr_page = None
    template_name = None

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
        rendered_page_text = page_text
        try:
            rendered_page_text = pre_renderer.get_pre_rendered_text()
        except PreRenderError as e:
            messages.error(self.request, e)

        return rendered_page_text


class NdrTemplateView(_NdrCoreView):
    """Basic template view. """


class _NdrCoreSearchView(_NdrCoreView):
    """ Base View for all NDR Core search views. A search view in this context means all views used to
     retrieve or display results. It is also the base view for all result download views."""

    form_class = AdvancedSearchForm

    def get_search_config_from_name(self, name):
        """ Convenience method to get search config. """
        try:
            if name == "simple" and self.ndr_page is not None:
                return self.ndr_page.search_configs.first()

            return NdrCoreSearchConfiguration.objects.get(conf_name=name)
        except NdrCoreSearchConfiguration.DoesNotExist:
            return None

    def fill_search_query_values(self, requested_search, query_obj):
        """ Translates the GET parameters provided by the search form to key-value pairs
        and saves them in the Query-object. """
        search_config = self.get_search_config_from_name(requested_search)
        form = self.form_class(self.request.GET, ndr_page=self.ndr_page, search_config=search_config)
        form.is_valid()

        for field in form.fields:
            if field.startswith(requested_search):
                # This removes the search conf name, leaving the actual field name
                actual_key = field[len(requested_search) + 1:]
                if search_config.search_form_fields.filter(search_field__field_name=actual_key).count() > 0:
                    query_obj.set_value(actual_key, form.cleaned_data[field])
                elif actual_key.endswith('condition'):
                    query_obj.set_value(actual_key, form.cleaned_data[field])
                else:
                    print("Invalid search field: " + actual_key)


class NdrDownloadView(_NdrCoreSearchView):
    """Returns a JSON record from an ID request to the API """

    def get(self, request, *args, **kwargs):
        api_factory = ApiFactory(self.get_search_config_from_name(self.kwargs['search_config']))
        api = api_factory.get_query_instance()
        record_id = url_deparse(self.kwargs['record_id'])
        query = api.get_record_query(record_id)
        result = api_factory.get_result_instance(query, self.request)
        result.load_result(transform_result=False)
        return JsonResponse(result.raw_result)


class NdrListDownloadView(_NdrCoreSearchView):
    """Returns a JSON record list from a search result. """

    def __init__(self):
        super().__init__()
        self.page_size = None

    def create_result_for_response(self):
        """Creates a result object for the response. """
        search_config = self.get_search_config_from_name(self.kwargs['search_config'])
        api_factory = ApiFactory(search_config)

        query_obj = api_factory.get_query_instance(page=self.request.GET.get("page", 1))
        self.fill_search_query_values(self.kwargs['search_config'], query_obj)
        query_string = query_obj.get_advanced_query()
        result = api_factory.get_result_instance(query_string, self.request)
        result.page_size = 250
        result.load_result(transform_result=False)

        return result

    def get(self, request, *args, **kwargs):
        result = self.create_result_for_response()
        return JsonResponse(result.raw_result['hits'], safe=False)


class NdrCSVListDownloadView(NdrListDownloadView):
    """Returns a CSV record list from a search result. """

    def get(self, request, *args, **kwargs):
        """Returns a CSV record list from a search result. """

        search_config = self.get_search_config_from_name(self.kwargs['search_config'])

        result = self.create_result_for_response()
        mapping = [
            {"field": search_config.search_id_field, "header": "ID"},
        ]
        search_config = self.get_search_config_from_name(self.kwargs['search_config'])
        for field in search_config.search_form_fields.all():
            if field.search_field.use_in_csv_export:
                mapping.append({"field": field.search_field.api_parameter, "header": field.search_field.field_label})

        csv_string = create_csv_export_string(result.raw_result['hits'], mapping)
        return HttpResponse(csv_string, content_type="text/csv")


class NdrMarkForCorrectionView(View):
    """Marks a record for correction. """

    def get(self, request, *args, **kwargs):
        """Marks a record for correction. """
        search_config = NdrCoreSearchConfiguration.objects.get(conf_name=self.kwargs['search_config'])
        NdrCoreCorrection.objects.create(corrected_dataset=search_config,
                                         corrected_record_id=url_deparse(self.kwargs['record_id']))
        return HttpResponse("OK")


class SearchView(_NdrCoreSearchView):
    """A view to search for records in the configured API. """

    def get(self, request, *args, **kwargs):
        """A view to search for records in the configured API. """
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
                if requested_search.endswith('_simple'):
                    requested_search_actual = requested_search[:-len('_simple')]
                    search_term = request.GET.get(f'search_term_{requested_search_actual}', '')
                    if search_term == '':
                        messages.error(request, _('Please enter a search term.'))
                        context.update({'form': form, 'requested_search': requested_search})
                        return render(request, self.template_name, context)

                    search_config = self.get_search_config_from_name(requested_search_actual)

                    api_factory = ApiFactory(search_config)
                    query_key = f"search_term_{search_config.conf_name}"
                    query_obj = api_factory.get_query_instance(page=request.GET.get("page", 1))
                    query_string = query_obj.get_simple_query(request.GET.get(query_key, ''),
                                                              request.GET.get("page", 1),
                                                              and_or=request.GET.get('and_or_field', 'and'))
                # An advanced search is called
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
                    context.update({'search_config': search_config})
                    context.update({'result': result})
                    is_compact = request.GET.get(f'compact_view_{requested_search}', 'normal')
                    if is_compact == "on":
                        is_compact = 'compact'
                    context.update({'result_card_group': is_compact})
        else:
            if "refine" in request.GET.keys():
                form = self.form_class(request.GET, ndr_page=self.ndr_page)

        context.update({'form': form, 'requested_search': requested_search})
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
        """Returns the context data for this view. """
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
        """Returns the context data for this view."""
        context = {}
        context.update(self.get_ndr_context_data())
        return context


def set_language_view(request, new_language):
    """A view to set the language of the page. """
    translation.activate(new_language)

    redirect_url = request.META.get('HTTP_REFERER')
    if redirect_url is None:
        redirect_url = reverse(f'{NdrSettings.APP_NAME}:index')

    response = HttpResponseRedirect(redirect_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, new_language)

    return response


def create_sitemap_view(request, as_string=False):
    """Create a sitemap.xml file. """
    pages = NdrCorePage.objects.all()
    context_pages = []
    for page in pages:
        page_obj = {
            'url': request.build_absolute_uri(page.url()),
            'lastmod': page.last_modified.isoformat(),
            'changefreq': 'monthly',
            'priority': 0.5,
        }
        if page.view_name == 'index':
            page_obj['priority'] = 1.0
        if page.page_type == NdrCorePage.PageType.SEARCH:
            page_obj['priority'] = 0.8
        elif page.page_type == NdrCorePage.PageType.CONTACT:
            page_obj['priority'] = 0.3
        elif page.page_type == NdrCorePage.PageType.ABOUT_PAGE:
            page_obj['priority'] = 0.3

        context_pages.append(page_obj)
    rendered = render_to_string('ndr_core/utils/sitemap.xml', {'pages': context_pages})
    if as_string:
        return rendered
    return HttpResponse(rendered, content_type='text/xml')


def create_robots_txt_view(request, as_string=False):
    """Create a robots.txt file."""
    sitemap_url = request.build_absolute_uri(reverse_lazy(f'{NdrSettings.APP_NAME}:sitemap'))
    text = f"""User-agent: *
Allow: /
    
Sitemap: { sitemap_url }"""

    if as_string:
        return text

    return HttpResponse(text, content_type='text/plain')


def manifest_url_view(request, manifest_id):
    """Returns a manifest URL. """
    try:
        manifest = NdrCoreManifest.objects.get(identifier=manifest_id)
    except NdrCoreManifest.DoesNotExist:
        return JsonResponse({'error': 'Manifest not found.'}, status=404)

    return JsonResponse({'manifest_url': manifest.file.url})


def google_search_console_verification_view(request, verification_file):
    """Returns a Google Search Console verification file. """

    # Open the file in the media folder
    # If it exists, return it, otherwise return a 404
    file_path = os.path.join(settings.MEDIA_ROOT, f"uploads/seo/google{verification_file}.html")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return HttpResponse(file.read())
    else:
        return render(request, 'ndr_core/404.html', status=404)