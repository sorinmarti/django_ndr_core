import json

import pymongo
import pymongo.errors
from bson import json_util
from django.utils.translation import gettext_lazy as _

from ndr_core.api.base_result import BaseResult


class MongoDBResult(BaseResult):
    """Simple implementation of the ninja-api API. """

    def download_result(self):
        try:
            connection_string = f"mongodb://{self.api_configuration.api_host}:{self.api_configuration.api_port}/"
            db_client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=2000)
            collection = db_client[self.api_configuration.api_url_stub][self.api_configuration.api_name]
            self.page = int(self.page)

            sort = list({'date.ref': 1 }.items())
            my_document = collection.find(filter=self.query,
                                          sort=sort,
                                          skip=self.page * self.page_size,
                                          limit=self.page_size)

            hits = []
            for hit in my_document:
                hit = json.loads(json_util.dumps(hit))
                hits.append(hit)

            self.raw_result = {
                "total": collection.count_documents(self.query),
                "page": self.page,
                "hits": hits
            }
        except pymongo.errors.ServerSelectionTimeoutError:
            self.error = _("Timed out")

    def save_raw_result(self, text):
        """ Normally this would save the raw result to a json object.
        In this case, the MongoClient is already returning a JSON object."""
        pass

    def fill_meta_data(self):
        self.total = self.raw_result["total"]
        self.page = self.raw_result["page"]
        self.page_size = self.api_configuration.api_page_size
        self.num_pages = self.total // self.page_size
        if self.total % self.page_size > 0:
            self.num_pages += 1

    def fill_results(self):
        self.results = self.raw_result['hits']

