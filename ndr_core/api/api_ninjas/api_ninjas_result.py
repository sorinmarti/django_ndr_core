"""Simple implementation of the ninja-api API. """
import json
from django.utils.translation import gettext_lazy as _
from ndr_core.api.base_result import BaseResult


class ApiNinjasResult(BaseResult):
    """Simple implementation of the ninja-api API. """

    def __init__(self, search_configuration, query, request):
        super().__init__(search_configuration, query, request)
        self.api_request_headers['X-Api-Key'] = self.search_configuration.api_auth_key

    def save_raw_result(self, text):
        """API Ninjas returns a JSON response. Save it as dict, so it can be accessed easily. """
        try:
            json_obj = json.loads(text)
            self.raw_result = json_obj
            return
        except json.JSONDecodeError:
            self.error = _("Result could not be loaded")
            self.error_code = BaseResult.LOADED
            return

    def fill_search_result_meta_data(self):
        """Set the metadata for the search result."""
        self.total = len(self.raw_result)
        self.page = 1
        self.page_size = self.total
        self.num_pages = 1

    def fill_results(self):
        """Fill the results with the raw result."""
        self.results = self.raw_result
