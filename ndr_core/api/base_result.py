""" This file contains the base result class. The base result class is used to
retrieve a result from a server, load it and transform it, so ndr-core can render it."""
from abc import ABC, abstractmethod

import requests
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ndr_core.geo_ip_utils import get_user_ip, get_geolocation
from ndr_core.models import (NdrCoreValue,
                             NdrCoreSearchStatisticEntry,
                             NdrCoreManifest,
                             NdrCoreUiElementItem,
                             NdrCorePage)
from ndr_core.templatetags.ndr_utils import url_parse
from ndr_core.ndr_templatetags.template_string import TemplateString


class BaseResult(ABC):
    """ The result class is used to retrieve a result from a server,
    load it and transform it, so ndr-core can render it.
    The result class is abstract and needs to be implemented for each API.
    Implementations are used as follows: Create instance -> call load_result() -> use result.
    """

    TIMEOUT = -100
    REQUEST = -101
    LOADED = -102
    SERVER = -103

    def __init__(self, search_configuration, query, request):
        if search_configuration is None:
            raise ValueError("search_configuration must not be None")

        self.search_configuration = search_configuration
        self.query = query
        self.request = request
        self.api_request_headers = {}
        self.raw_result = None
        self.error = None
        self.error_code = None

        self.total = 0
        self.page = 1
        self.page_size = self.search_configuration.page_size
        self.num_pages = 0
        self.page_links = {}
        self.form_links = {}
        self.results = []

    def load_result(self, transform_result=True):
        """Convenience function to undertake all the necessary steps to have a sanitized search result.
        This function is called by the view and should not be overwritten.
        :param transform_result: If true, the result is transformed to be rendered by the template."""

        # 1.) download the text and save it to self.raw_result
        self.download_result()
        if self.raw_result is None:
            # If the download failed, the error is already set.
            # This will return an empty result
            return

        # 2.) fill metadata (self.total, self.page, self.page_size, self.num_pages)
        self.fill_search_result_meta_data()

        # 3.) With the metadata known (current page, total results, etc.), create pagination links
        self.page_links = self.get_pagination_links()

        # 4.) Create links to refine search or start a new one
        self.form_links = self.get_form_links()

        # 5.) Fill the result list with dict objects. Each dict object represents a result.
        self.fill_results()

        if transform_result:
            # 5.) Transform the result to render it according to the configuration
            self.transform_results()

        # 6.) Log search
        self.log_search()

    def download_result(self):
        """Downloads the result by requesting the query.
        The result is saved in self.raw_result or an error is logged. """

        try:
            # Timeouts: 2s until connection, 5s until result
            result = requests.get(self.query, timeout=(2, 5), headers=self.api_request_headers)
        except requests.exceptions.ConnectTimeout:
            self.error = _("The connection timed out")
            self.error_code = BaseResult.TIMEOUT
            return
        except requests.exceptions.RequestException:
            self.error = _("Query could not be requested")
            self.error_code = BaseResult.REQUEST
            return

        # If request was successful: load json object from it
        if result.status_code == 200:
            self.save_raw_result(result.text)
        else:
            self.error = _(f"The server returned status code: {result.status_code}")
            self.error_code = BaseResult.SERVER
            return

    @abstractmethod
    def save_raw_result(self, text):
        """Save the raw text result in the desired form for post procession"""

    @abstractmethod
    def fill_search_result_meta_data(self):
        """Fill the meta-data variables from the raw result. NDR Core excepts the following variables:
        self.total: The total number of results
        self.page: The current page
        self.num_pages: The total number of pages
        """

    @abstractmethod
    def fill_results(self):
        """Fill the results list with dict objects. Each dict object represents a result.
        The dict object must contain the following keys:
        """

    def get_id_value(self, result):
        """ This function returns the id of a result. """
        return result[self.search_configuration.search_id_field]

    def get_result_options(self, result):
        """ This function creates the options for a result.
        If the download feature is turned on, a download button is added.
        If the correction feature is turned on, a correction button is added.
        If the data repository is configured, a link to the data repository is added.

        :param result: The record to create the options for
        :return: Return a list of dicts with the options for a result."""

        result_options = []
        record_id = url_parse(self.get_id_value(result))

        # Download single record
        if NdrCoreValue.get_or_initialize("search_allow_download_single",
                                          init_type=NdrCoreValue.ValueType.BOOLEAN,
                                          init_value="true").get_value():
            result_options.append({
                "href": reverse('ndr_core:download_record',
                                kwargs={'search_config': self.search_configuration.conf_name,
                                        'record_id': record_id}),
                "target": "_blank",
                "label": '<i class="fa-regular fa-file-arrow-down"></i>',
                "class": "btn btn-sm btn-secondary",
                "data-toggle": "tooltip",
                "data-placement": "top",
                "title": _("Download the record as a JSON file")
            })

        # Open Repository
        if self.search_configuration.repository_url is not None:
            result_options.append({
                "href": result['source']['collection'],
                "target": "_blank",
                "label": '<i class="fa-regular fa-vault"></i>',
                "class": "btn btn-sm btn-secondary",
                "data-toggle": "tooltip",
                "data-placement": "top",
                "title": _("View The Data Repository")
            })

        # Mark for Correction
        correction_feature = NdrCoreValue.get_or_initialize("correction_feature").get_value()
        if correction_feature:
            correction_url = reverse('ndr_core:mark_record',
                                     kwargs={'search_config': self.search_configuration.conf_name,
                                             'record_id': record_id})
            result_options.append({
                "onclick": f"callUrl('{correction_url}', '{record_id}')",
                "label": '<i class="fa-regular fa-check-double"></i>',
                "class": "btn btn-sm btn-secondary",
                "data-toggle": "tooltip",
                "data-placement": "top",
                "title": _("Report this entry as incorrect")
            })

        # Show Source
        # If a search config has a 'manifest_relation_expression', a button to view the source is added
        # In order for that to work, the manifest_relation_expression must point to a manifest id.
        # Then, the group this manifest belongs to has to be used in an ManifestViewer UI-Element
        # and the UI-Element has to be used on a page.
        if self.search_configuration.manifest_relation_expression is not None and \
                self.search_configuration.manifest_relation_expression != "":

            manifest_id_ts = TemplateString(self.search_configuration.manifest_relation_expression, result)
            page_number_ts = TemplateString(self.search_configuration.manifest_page_expression, result)

            try:
                # This is the manifest id as composed by the template string
                manifest_id = manifest_id_ts.get_formatted_string()
                # This is the manifest group object which is associated with the manifest
                manifest_group = NdrCoreManifest.objects.get(identifier=manifest_id).manifest_group
                # This is the first UI-Element which is associated with the manifest group
                first_ui_element = NdrCoreUiElementItem.objects.filter(manifest_group=manifest_group).first()

                if first_ui_element is not None:
                    first_page_w_ui_element = NdrCorePage.objects.filter(template_text__icontains=f"[[manifest_viewer|{first_ui_element.belongs_to.name}]]").first()
                    if first_page_w_ui_element is not None:
                        view_source_url = (reverse('ndr:ndr_view', kwargs={'ndr_page': first_page_w_ui_element.view_name}) +
                                           f"?manifest={manifest_id}&page={page_number_ts.get_formatted_string()}")

                        result_options.append({
                            "href": view_source_url,
                            "label": '<i class="fa-regular fa-book"></i>',
                            "class": "btn btn-sm btn-secondary",
                            "data-toggle": "tooltip",
                            "data-placement": "top",
                            "title": _("View this snippet in context")
                        })
            except NdrCoreManifest.DoesNotExist as e:
                pass

        # Copy Citation
        result_options.append({
            "onclick": f"copyToClipboard('{record_id}')",
            "label": '<i class="fa-regular fa-copy"></i>',
            "class": "btn btn-sm btn-secondary",
            "data-toggle": "tooltip",
            "data-placement": "top",
            "title": _("Copy Citation")
        })
        return result_options

    def transform_results(self):
        """Transforms the results to be rendered by the template.
        The results are transformed into a list of dicts. Each dict contains the following keys:
        id: The id of the result
        data: The data of the result
        result_meta: The result metadata (result_number, total_results)
        options: The options of the result (download, correction, etc.)
        """
        hit_number = self.page * self.page_size - self.page_size + 1

        transformed_results = []
        for result in self.results:
            transformed_result = {
                "id": self.get_id_value(result),
                "data": result,
                "result_meta": {
                    "result_number": hit_number,
                    "total_results": self.total
                },
                "options": self.get_result_options(result)
            }
            transformed_results.append(transformed_result)
            hit_number += 1

        self.results = transformed_results

    def log_search(self):
        """Logs the search to the database if the feature is turned on. """
        if NdrCoreValue.get_or_initialize('statistics_feature').get_value():
            location = get_geolocation(get_user_ip(self.request))
            search_term = ''

            NdrCoreSearchStatisticEntry.objects.create(search_config=self.search_configuration,
                                                       search_term=search_term,
                                                       search_query=self.query,
                                                       search_no_results=self.total,
                                                       search_location=location)

    def get_form_links(self):
        """Returns a dict with links to refine the search or start a new one."""
        form_links = {}

        # Refine URL
        updated_url = self.request.GET.copy()
        try:
            del updated_url[f'search_button_{self.search_configuration.conf_name}']
            if 'tab' in updated_url:
                del updated_url['tab']
        except KeyError:
            pass
        form_links['refine'] = (self.request.path + "?" + updated_url.urlencode() +
                                "&refine=1&tab=" + self.search_configuration.conf_name)

        # New Search URL
        form_links['new'] = self.request.path + "?tab=" + self.search_configuration.conf_name

        form_links['bulk_download_json'] = (
                reverse('ndr_core:download_list',
                        kwargs={'search_config': self.search_configuration.conf_name}) +
                "?" + updated_url.urlencode())

        form_links['bulk_download_csv'] = (
                reverse('ndr_core:download_csv',
                        kwargs={'search_config': self.search_configuration.conf_name}) +
                "?" + updated_url.urlencode())

        # Compact URL
        updated_url = self.request.GET.copy()
        possible_configs = [
            f'compact_view_{self.search_configuration.conf_name}',
            f'compact_view_{self.search_configuration.conf_name}_simple'
        ]

        for config in possible_configs:
            pass

        try:
            if f'compact_view_{self.search_configuration.conf_name}' in updated_url and \
                    f'search_button_{self.search_configuration.conf_name}' in updated_url:

                form_links['compact_label'] = _("Show full results")
                del updated_url[f'compact_view_{self.search_configuration.conf_name}']
                form_links['compact'] = (self.request.path + "?" + updated_url.urlencode())

            elif f'compact_view_{self.search_configuration.conf_name}_simple' in updated_url and \
                    f'search_button_{self.search_configuration.conf_name}_simple' in updated_url:
                form_links['compact_label'] = _("Show full results")
                del updated_url[f'compact_view_{self.search_configuration.conf_name}_simple']
                form_links['compact'] = (self.request.path + "?" + updated_url.urlencode())
            else:
                form_links['compact_label'] = _("Show compact results")
                if f'search_button_{self.search_configuration.conf_name}' in updated_url:
                    form_links['compact'] = (self.request.path + "?" + updated_url.urlencode() +
                                         "&compact_view_" + self.search_configuration.conf_name + "=on")
                elif f'search_button_{self.search_configuration.conf_name}_simple' in updated_url:
                    form_links['compact'] = (self.request.path + "?" + updated_url.urlencode() +
                                         "&compact_view_" + self.search_configuration.conf_name + "_simple=on")
                else:
                    form_links['compact'] = "ERROR"
                    """form_links['compact'] = (self.request.path + "?" + updated_url.urlencode() +
                                         "&compact_view_" + self.search_configuration.conf_name + "=on")"""
        except KeyError:
            pass

        return form_links

    def get_pagination_links(self):
        """Returns list of objects containing the page number and the url to the result page.
        If there are more than 8 Pages, only part of all pages are shown. This is used for
        pagination."""
        page_list = []

        if self.page <= 5 and self.num_pages >= 10:
            page_range = [str(x) for x in [*range(1, 8)]]
            page_list = page_range + ['...', str(self.num_pages)]
        else:
            if self.page + 4 == self.num_pages and self.num_pages > 5:
                page_range = [str(x) for x in [*range(self.page - 2, self.num_pages + 1)]]
                page_list = ['1', '...'] + page_range

            else:
                if self.num_pages < 10 and self.page < 10:
                    for number in range(self.num_pages):
                        page_list.append(str(number + 1))

                else:
                    if self.num_pages - 3 <= self.page:
                        page_list = ['1', '...']
                        page_range = [str(x) for x in [*range(self.num_pages - 6, self.num_pages + 1)]]
                        page_list.extend(page_range)

                    else:
                        page_range = [str(x) for x in [*range(self.page - 2, self.page + 3)]]
                        page_list = ['1', '...'] + page_range + ['...', str(self.num_pages)]

        enriched_page_list = []
        url = self.request.path + "?"

        for get_param in self.request.GET:
            if get_param != 'page':
                url += get_param + "=" + self.request.GET.get(get_param, "") + "&"

        for page in page_list:
            enriched_page_list.append({'page': page, 'url': url + "page=" + page})

        return {'pages': enriched_page_list,
                'prev': f"{url}page={self.page - 1}",
                'next': f"{url}page={self.page + 1}"}

    @staticmethod
    def safe_get(dct, keys):
        """ Helper function to get nested keys"""
        for key in keys:
            try:
                dct = dct[key]
            except KeyError:
                return None
        return dct
