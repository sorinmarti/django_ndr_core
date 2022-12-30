import json

from ndr_core.api.base_result import BaseResult
from django.utils.translation import gettext_lazy as _


class NdrCoreResult(BaseResult):

    def save_raw_result(self, text):
        """NDR Core returns a JSON response. Save it as dict, so it can be accessed easily. """
        try:
            json_obj = json.loads(text)
            self.raw_result = json_obj
            return
        except json.JSONDecodeError:
            self.error = _("Result could not be loaded")
            self.error_code = BaseResult.LOADED
            return

    def fill_meta_data(self):
        """Set the meta data. """
        self.total = int(self.raw_result['total'])
        self.page = int(self.raw_result['page'])
        self.page_size = int(self.raw_result['size'])
        self.num_pages = int(self.total / self.page_size)
        if int(self.total) % int(self.page_size) > 0:
            self.num_pages += 1

    def fill_results(self):
        """Fill the raw results list."""
        for result in self.raw_result['hits']:
            self.results.append(result)
