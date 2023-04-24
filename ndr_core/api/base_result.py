from abc import ABC, abstractmethod
import json

import requests
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ndr_core.geo_ip_utils import get_user_ip, get_geolocation
from ndr_core.models import NdrCoreValue, NdrCoreSearchStatisticEntry
from ndr_core.templatetags.ndr_utils import url_parse


class BaseResult(ABC):
    """ The result class is used to actually retrieve a result from a server,
    load it and transform it, so ndr-core can render it."""

    TIMEOUT = -100
    REQUEST = -101
    LOADED = -102
    SERVER = -103

    def __init__(self, search_configuration, query, request):
        if search_configuration is None:
            raise ValueError("search_configuration must not be None")
        if search_configuration.api_configuration is None:
            raise ValueError("api_configuration must not be None")

        self.search_configuration = search_configuration
        self.api_configuration = self.search_configuration.api_configuration
        self.query = query
        self.request = request
        self.api_request_headers = {}
        self.raw_result = None
        self.error = None
        self.error_code = None

        self.total = 0
        self.page = 1
        self.page_size = self.api_configuration.api_page_size
        self.num_pages = 0
        self.page_links = {}
        self.form_links = {}
        self.results = list()

    def load_result(self, transform_result=True):
        """Convenience function to undertake all the necessary steps to have a sanitized search result."""
        # 1.) download the text and save it to self.raw_result
        self.download_result()
        if self.raw_result is None:
            return

        # 2.) fill meta data (self.total, self.page, self.page_size, self.num_pages)
        self.fill_meta_data()

        # 3.) With the metadata known (current page, total results, etc.), create pagination links
        self.page_links = self.get_page_list()

        # 4.) Create links to refine search or start a new one
        self.form_links = self.get_form_links()

        # 4.) Fill the result list with dict objects
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
        except requests.exceptions.ConnectTimeout as e:
            self.error = _("The connection timed out")
            self.error_code = BaseResult.TIMEOUT
            return
        except requests.exceptions.RequestException as e:
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
        pass

    @abstractmethod
    def fill_meta_data(self):
        """Fill the meta-data variables from the raw result"""
        pass

    @abstractmethod
    def fill_results(self):
        """Fill the actual results from the search in the hit list"""
        pass

    def get_result_options(self, record_id):
        """
        :param record_id: The id of the record to create the options for
        :return: Return a list of dicts with the options for a result."""

        result_options = []
        if NdrCoreValue.get_or_initialize("search_allow_download_single",
                                          init_type=NdrCoreValue.ValueType.BOOLEAN,
                                          init_value="true").get_value():
            result_options.append({
                "href": reverse('ndr_core:download_record',
                                kwargs={'search_config': self.search_configuration.conf_name,
                                        'record_id': url_parse(record_id)}),
                "target": "_blank",
                "label": '<i class="fa-regular fa-file-arrow-down"></i>',
                "class": "btn btn-sm btn-secondary",
                "data-toggle": "tooltip",
                "data-placement": "top",
                "title": "Download the record as a JSON file"
            })

        if self.api_configuration.api_repository_url is not None:
            result_options.append({
                "href": self.api_configuration.api_repository_url,
                "target": "_blank",
                "label": '<i class="fa-regular fa-vault"></i>',
                "class": "btn btn-sm btn-secondary",
                "data-toggle": "tooltip",
                "data-placement": "top",
                "title": "View The Data Repository"
            })

        correction_feature = NdrCoreValue.get_or_initialize("correction_feature").get_value()
        if correction_feature:
            correction_url = reverse('ndr_core:mark_record',
                                     kwargs={'api_config': self.api_configuration.api_name,
                                             'record_id': url_parse(record_id)})
            result_options.append({
                "onclick": f"callUrl('{correction_url}', '{url_parse(record_id)}')",
                "label": '<i class="fa-regular fa-check-double"></i>',
                "class": "btn btn-sm btn-secondary",
                "data-toggle": "tooltip",
                "data-placement": "top",
                "title": "Report this entry as incorrect"
            })

        result_options.append({
            "onclick": f"copyToClipboard('{url_parse(record_id)}')",
            "label": '<i class="fa-regular fa-copy"></i>',
            "class": "btn btn-sm btn-secondary",
            "data-toggle": "tooltip",
            "data-placement": "top",
            "title": "Copy Citation"
        })
        return result_options

    def transform_results(self):
        hit_number = self.page * self.page_size - self.page_size + 1

        transformed_results = list()
        for result in self.results:
            transformed_result = {
                "id": "",
                "title": "",
                "transcription": "",
                "values": [],
                "result_meta": {
                    "result_number": hit_number,
                    "total_results": self.total
                },
                "original_data": result,
                "data_string": json.dumps(result, indent=4),
                "options": self.get_result_options(result['source']['selector']['id'])  # TODO: Make this generic
            }
            transformed_results.append(transformed_result)
            hit_number += 1

        self.results = transformed_results

    def log_search(self):
        """Logs the search to the database if the feature is turned on. """
        if NdrCoreValue.get_or_initialize('statistics_feature').get_value():
            location = get_geolocation(get_user_ip(self.request))
            search_term = ''

            NdrCoreSearchStatisticEntry.objects.create(search_api=self.api_configuration,
                                                       search_term=search_term,
                                                       search_query=self.query,
                                                       search_no_results=self.total,
                                                       search_location=location)

    def organize_raw_result_old(self):
        # Actual results of this page
        # TODO: Add Ndr core data: has_page_image,page_image, has_fragment, fragment, result_number, total_results
        self.results = self.get_transformed_hits()

    def get_transformed_hits(self):
        # TODO
        results = list()
        hit_number = self.page * self.page_size - self.page_size + 1
        for hit in self.raw_result['hits']:
            transformed_data = {
                "options": [],
                "values": []
            }
            transformer = [
                {
                    "target_field_name": "transcription",
                    "source_field_name": "transcription.corrected",
                    "dne_field_name": "transcription.original",
                    "none_value": "<no data>",
                    "field_label": "Transcription"
                },
                {
                    "target_field_name": "date",
                    "source_field_name": "date.ref",
                    "none_value": "<no data>"
                },
                {
                    "target_field_name": "status",
                    "source_field_name": "status",
                    "none_value": "<no data>"
                },
                {
                    "target_field_name": "status",
                    "source_field_name": "status",
                    "none_value": "<no data>"
                },
                {
                    "target_field_name": "Locations",
                    "source_field_name": "location",
                    "field_type": "list",
                    "list_key": "transcription"
                },
                {
                    "target_field_name": "page_image",
                    "source_field_name": "source.selector.canvas",
                    "field_type": "page_image"
                },
                {
                    "target_field_name": "fragment_image",
                    "source_field_name": "source.selector.fragment",
                    "field_type": "fragment_image"
                }
            ]

            for transform_action in transformer:
                key_parts = transform_action["source_field_name"].split(".")
                desired_value = BaseResult.safe_get(hit, key_parts)
                if desired_value is None and "dne_field_name" in transform_action:
                    key_parts = transform_action["dne_field_name"].split(".")
                    desired_value = BaseResult.safe_get(hit, key_parts)
                if desired_value is None and "none_value" in transform_action:
                    desired_value = transform_action["none_value"]

                if "field_type" not in transform_action or transform_action["field_type"] == "default":
                    field_label = transform_action["target_field_name"]
                    if "field_label" in transform_action:
                        field_label = transform_action["field_label"]
                    transformed_data["values"].append({"value": desired_value, "label": field_label})
                else:
                    transformed_data[transform_action["target_field_name"]] = desired_value

                    if desired_value is not None:
                        if transform_action["field_type"] == "list":
                            transformed_data[transform_action["target_field_name"]] = ", ".join([x["transcription"] for x in desired_value])
                            transformed_data["values"].append({"value": ", ".join([x["transcription"] for x in desired_value]), "label": "Loc"})
                        if transform_action["field_type"] == "page_image":
                            transformed_data["has_page_image"] = True
                        if transform_action["field_type"] == "fragment_image":
                            transformed_data["has_fragment_image"] = True


            # TODO Options
            transformed_data["options"] = [
                {
                    "url": reverse('ndr_core:download_record', kwargs={'api_config': self.api_configuration.api_name, 'record_id': hit['id']}),
                    "target": "_blank", "label": "View Repository"
                },
                {
                    "url": "http:",
                    "target": "_blank", "label": "label"
                }
            ]

            hit["ndr"] = transformed_data
            results.append(hit)
            hit_number += 1
        return results

    def get_form_links(self):
        form_links = {}

        # Refine URL
        updated_url = self.request.GET.copy()
        try:
            del (updated_url[f'search_button_{self.search_configuration.conf_name}'])
            if 'tab' in updated_url:
                del (updated_url['tab'])
        except KeyError:
            pass
        form_links['refine'] = self.request.path + "?" + updated_url.urlencode() + "&tab=" + self.search_configuration.conf_name

        # New Search URL (TODO change this to view name)
        form_links['new'] = self.request.path

        form_links['bulk_download_json'] = reverse('ndr_core:download_list',
                                                   kwargs={'search_config': self.search_configuration.conf_name}) + "?" + updated_url.urlencode()

        form_links['bulk_download_csv'] = reverse('ndr_core:download_csv',
                                                  kwargs={'search_config': self.search_configuration.conf_name}) + "?" + updated_url.urlencode()
        return form_links

    def get_page_list(self):
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

        enriched_page_list = list()
        url = self.request.path + "?"

        for get_param in self.request.GET:
            if get_param != 'page':
                url += get_param + "=" + self.request.GET.get(get_param, "") + "&"

        for page in page_list:
            enriched_page_list.append({'page': page, 'url': url + "page=" + page})

        return {'pages': enriched_page_list, 'prev': f"{url}page={self.page - 1}",
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
