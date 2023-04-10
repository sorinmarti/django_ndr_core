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

            if 'type' in self.query and self.query['type'] is 'single':
                my_document = collection.find_one(filter=self.query['filter'])
                self.raw_result = json.loads(json_util.dumps(my_document))
                return

            try:
                self.page = self.query['page']
            except KeyError:
                self.page = 0

            my_document = collection.find(filter=self.query['filter'],
                                          sort=self.query['sort'],
                                          skip=self.page * self.page_size - self.page_size,
                                          limit=self.page_size)

            hits = []
            for hit in my_document:
                hit = json.loads(json_util.dumps(hit))
                hits.append(hit)

            total_count = collection.count_documents(self.query['filter'])
            self.raw_result = {
                "total": total_count,
                "page": self.page,
                "hits": hits
            }
            # print(self.raw_result)
        except pymongo.errors.ServerSelectionTimeoutError:
            self.error = _("Timed out")

    def save_raw_result(self, text):
        """ Normally this would save the raw result to a json object.
        In this case, the MongoClient is already returning a JSON object."""
        pass

    def fill_meta_data(self):
        """Fills the meta data from the raw result"""
        if "total" in self.raw_result:
            self.total = self.raw_result["total"]
        else:
            self.total = 0
        if "page" in self.raw_result:
            self.page = self.raw_result["page"]

        self.num_pages = self.total // self.page_size
        if self.total % self.page_size > 0:
            self.num_pages += 1

    def fill_results(self):
        if "hits" in self.raw_result:
            self.results = self.raw_result['hits']

