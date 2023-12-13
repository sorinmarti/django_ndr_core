"""Implementation of the MongoDBResult class. """
import json

import pymongo
import pymongo.errors
from bson import json_util
from django.utils.translation import gettext_lazy as _

from ndr_core.api.base_result import BaseResult
from ndr_core.utils import get_nested_value


class MongoDBResult(BaseResult):
    """Implementation of the mongo DB API. """

    def download_result(self):
        """Retrieves the result from the MongoDB."""

        try:
            # Get the connection string and collection from the configuration
            connection_string_arr = self.search_configuration.api_connection_url.split('/')
            connection_string = '/'.join(connection_string_arr[:-1])
            db_client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=2000)
            collection = db_client[connection_string_arr[-2]][connection_string_arr[-1]]

            # If the query is a single document, return the raw result to be downloaded.
            if 'type' in self.query and self.query['type'] == 'single':
                my_document = collection.find_one(filter=self.query['filter'])
                self.raw_result = json.loads(json_util.dumps(my_document))
                return

            # Check if the page number is specified, otherwise set it to 0
            try:
                self.page = self.query['page']
            except KeyError:
                self.page = 0

            # Calculate the number of documents to skip in order to get the correct list. Size of the list is page_size
            # and the page number is 1-based.
            skip = self.page * self.page_size - self.page_size

            # Retrieve the documents from the collection
            my_document = collection.find(filter=self.query['filter'],
                                          sort=self.query['sort'],
                                          skip=skip,
                                          limit=self.page_size)

            # Convert the documents to a list of dictionaries
            hits = []
            for hit in my_document:
                hit = json.loads(json_util.dumps(hit))
                hits.append(hit)

            # Get the total number of documents in the result
            total_count = collection.count_documents(self.query['filter'])

            # Create the raw result
            self.raw_result = {
                "total": total_count,
                "page": self.page,
                "hits": hits
            }

        except pymongo.errors.ServerSelectionTimeoutError:
            self.error = _("Timed out")

    def save_raw_result(self, text):
        """ Normally this would save the raw result to a json object.
        In this case, the MongoClient is already returning a JSON object."""

    def fill_search_result_meta_data(self):
        """Fills the search result metadata. In the download_result method, the raw result is created and the
        total number of documents is retrieved. The page number is also set in the download_result method."""

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

    def get_id_value(self, result):
        """ Overwrite the default get_id_value method to get the id from the result. """
        return get_nested_value(result, self.search_configuration.search_id_field)
