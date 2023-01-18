import json
import pymongo
from django.utils.translation import gettext_lazy as _
from ndr_core.api.base_result import BaseResult


class MongoDBResult(BaseResult):
    """Simple implementation of the ninja-api API. """

    def save_raw_result(self, text):
        """API Ninjas returns a JSON response. Save it as dict, so it can be accessed easily. """
        db_client = pymongo.MongoClient("mongodb://localhost:27017/")
        my_db = db_client["bscc"]
        my_col = my_db["1951"]

        my_query = {"id": "BSCC-14-1951-2-A3"}
        my_doc = my_col.find(my_query)

        for x in my_doc:
            print(x)
        try:
            json_obj = json.loads(text)
            self.raw_result = json_obj
            return
        except json.JSONDecodeError:
            self.error = _("Result could not be loaded")
            self.error_code = BaseResult.LOADED
            return

    def fill_meta_data(self):
        self.total = len(self.raw_result)
        self.page = 1
        self.page_size = self.total
        self.num_pages = 1

    def fill_results(self):
        self.results = self.raw_result

