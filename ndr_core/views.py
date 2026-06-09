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
from ndr_core.forms.forms_search import AdvancedSearchForm, DataListSearchForm

from ndr_core.models import (
    NdrCorePage,
    NdrCoreUserMessage,
    NdrCoreImage,
    NdrCoreCorrection,
    NdrCoreSearchConfiguration,
    NdrCoreValue,
    NdrCoreManifest
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
        NdrCorePage.PageType.DATA_LIST: DataListView,
        NdrCorePage.PageType.CONTACT: ContactView,
        NdrCorePage.PageType.FLIP_BOOK: FlipBookView,
        NdrCorePage.PageType.ABOUT_PAGE: AboutUsView,
        NdrCorePage.PageType.FULLSCREEN: FullScreenView,
    }

    if page_type not in translator:
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
    if request.path == reverse_lazy(f'{NdrSettings.APP_NAME}:html_page'):
        return return_static_html(request)

    page_is_under_construction = NdrCoreValue.get_or_initialize("under_construction",
                                                                init_type=NdrCoreValue.ValueType.BOOLEAN,
                                                                init_value="false").get_value()

    if page_is_under_construction:
        return TemplateView.as_view(template_name='ndr_core/under_construction.html')(request)

    if ndr_page is None:
        ndr_page = 'index'

    # Traverse path segments to find the page, supporting hierarchical URLs
    # e.g. 'datasets/a' -> find root page 'datasets', then child 'a'
    segments = ndr_page.split('/')
    page = None
    parent = None
    try:
        for segment in segments:
            page = NdrCorePage.objects.get(view_name=segment, parent_page=parent)
            parent = page
    except NdrCorePage.DoesNotExist:
        return TemplateView.as_view(template_name='ndr_core/404.html')(request, status=404)

    try:
        view_class = get_page_type_view_class(page.page_type)
        return view_class.as_view(template_name=f'{NdrSettings.APP_NAME}/{page.get_full_path()}.html',
                                  ndr_page=page)(request)
    except NdrCorePageNotFound:
        return TemplateView.as_view(template_name='ndr_core/404.html')(request, status=404)


def display_schema_or_404(request, schema_name):
    """Displays a schema or 404."""

    # Find the schema in the media files
    # If it exists, display it, otherwise display a 404

    schema_path = NdrSettings.get_schema_path()
    if schema_name in os.listdir(schema_path):
        with open(f'{schema_path}/{schema_name}', 'r', encoding='utf-8') as schema_file:
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
        # Get partner logos from settings
        from ndr_core.models import NdrCoreValue
        partner_logos_setting = NdrCoreValue.get_or_initialize('footer_partner_logo_images')
        partner_ids = [x.strip() for x in partner_logos_setting.value_value.split(',') if x.strip()]
        partners = NdrCoreImage.objects.filter(pk__in=partner_ids, image_active=True) if partner_ids else []

        # Get resolved background settings for this page
        page_background = self.ndr_page.get_resolved_background_settings()

        context = {'page': self.ndr_page,
                   'rendered_text': self.pre_render_text(),
                   'navigation': NdrCorePage.objects.filter(parent_page=None, show_in_navigation=True).order_by('index'),
                   'partners': partners,
                   'page_background': page_background}
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


class FullScreenView(_NdrCoreView):
    """Full screen page — renders only the template text with no navigation, footer, or container wrapper."""

    def get(self, request, *args, **kwargs):
        context = {'rendered_text': self.pre_render_text(), 'page': self.ndr_page}
        return render(request, self.template_name, context)


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
                elif actual_key.endswith('operator'):
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

    def build_search_explanation(self, form, requested_search, search_config):
        """Build a human-readable explanation of what was searched for."""
        explanations = []

        for field_name, value in form.cleaned_data.items():
            if not field_name.startswith(requested_search):
                continue
            if value in [None, '', [], False]:
                continue

            actual_field_name = field_name[len(requested_search) + 1:]

            # Skip modifier/meta fields — they're not search terms
            if actual_field_name.endswith(('_condition', '_operator')):
                continue
            if actual_field_name.startswith(('compact_view_', 'and_or_field_')):
                continue

            try:
                field_config = search_config.search_form_fields.get(
                    search_field__field_name=actual_field_name
                )
                search_field = field_config.search_field
                field_label = search_field.field_label

                # Resolve choice keys to human-readable labels
                if search_field.is_choice_field():
                    choices_dict = search_field.get_choices_list_dict()

                    def _resolve(v):
                        # BOOLEAN_LIST values have format "key__true" or "key__false"
                        key = v.split('__')[0] if '__' in str(v) else str(v)
                        entry = choices_dict.get(key)
                        return entry.get('value', key) if entry else key

                    if isinstance(value, list):
                        formatted_value = ', '.join(_resolve(v) for v in value)
                    else:
                        formatted_value = _resolve(value)

                # NumberRange returns a sorted list of ints — show as compact range
                elif isinstance(value, list) and value:
                    if len(value) == 1:
                        formatted_value = str(value[0])
                    else:
                        formatted_value = f'{value[0]}–{value[-1]}'

                else:
                    formatted_value = str(value)

                explanations.append(f'{field_label}: {formatted_value}')
            except Exception:
                continue

        return ' | '.join(explanations) if explanations else 'all available fields'

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
                # ------------------------------------------------------------------ #
                # Combined simple search: one term, multiple configs, merged results  #
                # ------------------------------------------------------------------ #
                if requested_search == 'combined_simple':
                    search_term = request.GET.get('search_term_combined_simple', '').strip()
                    if not search_term:
                        messages.error(request, _('Please enter a search term.'))
                        context.update({'form': form, 'requested_search': requested_search})
                        return render(request, self.template_name, context)

                    and_or = request.GET.get('and_or_field_combined_simple', 'and')
                    page = int(request.GET.get('page', 1))
                    master_config = self.ndr_page.combined_simple_search_config

                    combined_results = []  # list of {'data': <full result dict>, 'search_config': conf}
                    total_combined = 0

                    for conf in self.ndr_page.search_configs.filter(has_simple_search=True):
                        try:
                            api_factory = ApiFactory(conf)
                            query_obj = api_factory.get_query_instance(page=page)
                            query_string = query_obj.get_simple_query(
                                search_term, page, and_or=and_or
                            )
                            result_obj = api_factory.get_result_instance(query_string, self.request)
                            result_obj.load_result()
                            total_combined += result_obj.total
                            for item in result_obj.results:
                                combined_results.append({
                                    'data': item,  # full transformed dict: id, data, result_meta, options
                                    'search_config': conf,
                                })
                        except Exception:
                            pass

                    if not combined_results:
                        messages.error(request, _('No results found.'))
                    else:
                        # Sort merged list by master config's sort_field
                        sort_field = master_config.sort_field if master_config else None
                        if sort_field:
                            reverse_sort = (master_config.sort_order == 'desc') if master_config else False
                            combined_results.sort(
                                key=lambda r: r['data']['data'].get(sort_field, ''),
                                reverse=reverse_sort,
                            )
                        compact_checked = request.GET.get('compact_view_combined_simple', 'off') == 'on'
                        initial_compact = compact_checked if (master_config and master_config.search_has_compact_result) else False
                        context.update({
                            'combined_results': combined_results,
                            'combined_total': total_combined,
                            'search_explanation': search_term,
                            'initial_compact_view': initial_compact,
                            'combined_has_compact': master_config.search_has_compact_result if master_config else False,
                        })

                # The search is a per-config simple search
                elif requested_search.endswith('_simple'):
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

                    # Create a result object and load the result
                    result = api_factory.get_result_instance(query_string, self.request)
                    result.load_result()

                    if result.total == 0:
                        messages.error(request, _('No results found.'))
                    else:
                        context.update({'search_config': search_config})
                        context.update({'result': result})
                        compact_checked = (
                            request.GET.get(f'compact_view_{search_config.conf_name}', 'off') == 'on'
                            or request.GET.get(f'compact_view_{search_config.conf_name}_simple', 'off') == 'on'
                        )
                        initial_compact = compact_checked if search_config.search_has_compact_result else False
                        context.update({'initial_compact_view': initial_compact})
                        search_explanation = self.build_search_explanation(form, requested_search, search_config)
                        context.update({'search_explanation': search_explanation})

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
                        # Determine initial compact view state: checkbox in form overrides model default
                        conf = search_config.conf_name
                        compact_checked = (
                            request.GET.get(f'compact_view_{conf}', 'off') == 'on'
                            or request.GET.get(f'compact_view_{conf}_simple', 'off') == 'on'
                        )
                        initial_compact = compact_checked if search_config.search_has_compact_result else False
                        context.update({'initial_compact_view': initial_compact})

                        # Add search explanation for results summary
                        search_explanation = self.build_search_explanation(form, requested_search, search_config)
                        context.update({'search_explanation': search_explanation})
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

        # Team members should now be configured via UI Elements (e.g., people cards)
        # instead of directly from the image library
        team_members = []
        context['data'] = {'team_members': team_members}

        return render(request, self.template_name, context)


class DataListView(_NdrCoreSearchView):
    """A view to display a paginated list of all items from a search configuration.
    Uses compact result cards for list items, detailed cards for detail view,
    and simple search fields for filters."""

    form_class = DataListSearchForm

    def get(self, request, *args, **kwargs):
        """Display paginated list with optional filters."""
        context = self.get_ndr_context_data()

        # Get the single search config for this page
        search_config = self.ndr_page.search_configs.first()

        if not search_config:
            messages.error(request, _('No search configuration found for this data list page.'))
            return render(request, self.template_name, context)

        # Initialize form for filters
        form = self.form_class(ndr_page=self.ndr_page, search_config=search_config)

        # Create API factory and query
        api_factory = ApiFactory(search_config)
        query_obj = api_factory.get_query_instance(page=request.GET.get("page", 1))

        # Check if search term filter is applied
        search_term = None
        detail_page_id = None

        if request.GET:
            form = self.form_class(request.GET, ndr_page=self.ndr_page, search_config=search_config)
            if form.is_valid():
                search_term = form.cleaned_data.get('search_term', '').strip()
            if request.GET.get('id',''):
                detail_page_id = request.GET.get('id','').strip()

        # Apply data list filters (pre-filters with initial values)
        data_list_filters = search_config.data_list_filters.all()
        for filter_field in data_list_filters:
            if filter_field.initial_value:
                query_obj.set_value(filter_field.field_name, filter_field.initial_value)

        # Get query string - use appropriate query based on context
        if detail_page_id:
            query_string = query_obj.get_record_query(detail_page_id)
        elif search_term:
            query_string = query_obj.get_simple_query(search_term)
        elif data_list_filters.exists():
            # If we have data list filters, use advanced query to apply them
            query_string = query_obj.get_advanced_query()
        else:
            query_string = query_obj.get_all_items_query()

        # Create result object and load results
        result = api_factory.get_result_instance(query_string, self.request)
        result.load_result()
        print(result.total)

        # Add to context
        context.update({
            'form': form,
            'search_config': search_config,
            'result': result,
            'detail_page_id': detail_page_id,
            'search_term': search_term or '',
        })

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


def return_static_html(request):
    """Returns a static HTML page. """
    url_path = request.path
    file_name = url_path.split('/')[-1]
    file_path = f'{NdrSettings.get_images_path()}/{file_name}'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return HttpResponse(file.read(), content_type='text/html')

    return render(request, 'ndr_core/404.html', status=404)


def google_search_console_verification_view(request, verification_file):
    """Returns a Google Search Console verification file. """

    # Open the file in the media folder
    # If it exists, return it, otherwise return a 404
    file_path = os.path.join(settings.MEDIA_ROOT, f"uploads/seo/google{verification_file}.html")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return HttpResponse(file.read())
    else:
        return render(request, 'ndr_core/404.html', status=404)


def atlas_autocomplete_view(request, search_config):
    """Returns Atlas Search autocomplete suggestions as a JSON array.

    GET parameters:
      q  --  the prefix typed by the user (minimum 2 characters)

    The field to autocomplete is taken from api_settings['mongodb']['atlas_autocomplete_path'].
    It must be indexed with type: autocomplete in the Atlas Search index.

    Usage in a result template:
      Add a <datalist id="ndr-ac-{conf_name}"> and point the search input to it.
      The NDR Core JS (ndr_autocomplete.js) handles this automatically when
      data-ndr-autocomplete="{conf_name}" is present on the search input.
    """
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse([], safe=False)

    try:
        config = NdrCoreSearchConfiguration.objects.get(conf_name=search_config)
    except NdrCoreSearchConfiguration.DoesNotExist:
        return JsonResponse([], safe=False)

    mongodb_settings = (config.api_settings or {}).get('mongodb', {})
    if not mongodb_settings.get('use_atlas_search'):
        return JsonResponse([], safe=False)

    autocomplete_path = mongodb_settings.get('atlas_autocomplete_path', '').strip()
    if not autocomplete_path:
        return JsonResponse([], safe=False)

    try:
        import pymongo

        raw_url = config.api_connection_url.split('?')[0].rstrip('/')
        parts = raw_url.split('/')
        connection_string = '/'.join(parts[:-2])
        db_name = parts[-2]
        collection_name = parts[-1]

        client = pymongo.MongoClient(
            connection_string,
            username=config.api_user_name or None,
            password=config.api_password or None,
            serverSelectionTimeoutMS=10000,
        )
        collection = client[db_name][collection_name]

        pipeline = [
            {"$search": {
                "index": mongodb_settings.get('atlas_search_index') or 'default',
                "autocomplete": {"query": q, "path": autocomplete_path}
            }},
            {"$limit": 8},
            {"$project": {"_id": 0, autocomplete_path: 1}},
        ]

        suggestions = []
        for doc in collection.aggregate(pipeline):
            val = doc
            for key in autocomplete_path.split('.'):
                val = val.get(key) if isinstance(val, dict) else None
                if val is None:
                    break
            if isinstance(val, str):
                suggestions.append(val)

        return JsonResponse(suggestions, safe=False)

    except Exception:
        return JsonResponse([], safe=False)
