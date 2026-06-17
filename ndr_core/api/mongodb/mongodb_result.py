"""Implementation of the MongoDBResult class. """
import html as _html
import json
import logging

import pymongo
import pymongo.errors
from bson import json_util
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def _set_nested_value(d, keys, value):
    """Write *value* into nested dict *d* following the *keys* path."""
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value


def _build_highlight_html(texts):
    """Convert an Atlas Search highlight texts list to HTML with <mark> tags."""
    parts = []
    for item in texts:
        escaped = _html.escape(str(item.get('value', '')))
        if item.get('type') == 'hit':
            parts.append(f'<mark>{escaped}</mark>')
        else:
            parts.append(escaped)
    return ''.join(parts)

from ndr_core.api.base_result import BaseResult
from ndr_core.utils import get_nested_value


class MongoDBResult(BaseResult):
    """Implementation of the mongo DB API. """

    def download_result(self):
        """Retrieves the result from the MongoDB."""

        try:
            # Parse connection URL: <protocol>://<host>/<db>/<collection>
            # Strip query parameters before splitting (e.g. ?appName=... from Atlas URLs)
            raw_url = self.search_configuration.api_connection_url.split('?')[0].rstrip('/')
            connection_string_arr = raw_url.split('/')
            connection_string = '/'.join(connection_string_arr[:-2])
            db_name = connection_string_arr[-2]
            collection_name = connection_string_arr[-1]

            # Use a longer timeout for Atlas (SRV) connections than for local ones
            timeout_ms = 30000 if connection_string.startswith('mongodb+srv') else 2000

            # Pass credentials when provided
            username = self.search_configuration.api_user_name or None
            password = self.search_configuration.api_password or None
            db_client = pymongo.MongoClient(
                connection_string,
                username=username,
                password=password,
                serverSelectionTimeoutMS=timeout_ms,
            )
            collection = db_client[db_name][collection_name]

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

            # Atlas Search: run aggregation pipeline (built by _build_atlas_search_query)
            if self.query.get('type') == 'atlas_search':
                cursor = collection.aggregate(self.query['pipeline'])
                facet_result = next(cursor, {})
                hits = []
                for raw_hit in facet_result.get('hits', []):
                    hit = json.loads(json_util.dumps(raw_hit))
                    # Extract _searchHighlights (materialized from $meta before $facet)
                    search_highlights = hit.pop('_searchHighlights', [])
                    if search_highlights:
                        hl_dict = {}
                        for hl in search_highlights:
                            _set_nested_value(
                                hl_dict,
                                hl['path'].split('.'),
                                _build_highlight_html(hl.get('texts', []))
                            )
                        hit['_hl'] = hl_dict
                    hits.append(hit)
                total_list = facet_result.get('total', [])
                total_count = total_list[0]['count'] if total_list else 0
                self.raw_result = {
                    "total": total_count,
                    "page": self.page,
                    "hits": hits
                }
                return

            # Single $facet aggregation: one scan for both the page of hits and the total count.
            # (Two separate find() + count_documents() calls would scan the collection twice.)
            skip = self.page * self.page_size - self.page_size
            pipeline = [
                {"$match": self.query['filter']},
                {"$sort": dict(self.query['sort'])},
                {"$facet": {
                    "hits":  [{"$skip": skip}, {"$limit": self.page_size}],
                    "total": [{"$count": "count"}],
                }},
            ]
            facet_result = next(collection.aggregate(pipeline), {})
            hits = [json.loads(json_util.dumps(h)) for h in facet_result.get('hits', [])]
            total_count = (facet_result.get('total') or [{}])[0].get('count', 0)

            self.raw_result = {
                "total": total_count,
                "page": self.page,
                "hits": hits,
            }

        except pymongo.errors.ServerSelectionTimeoutError as e:
            self.error = _("Timed out")
            print(f"[MongoDB] ServerSelectionTimeoutError: {e}")
            logger.error("MongoDB server selection timed out: %s", e)
        except pymongo.errors.OperationFailure as e:
            self.error = f"MongoDB operation failed: {e.details.get('errmsg', str(e))}"
            print(f"[MongoDB] OperationFailure (code {e.code}): {e}")
            logger.error("MongoDB operation failure (code %s): %s", e.code, e)
        except pymongo.errors.ConfigurationError as e:
            self.error = f"MongoDB configuration error: {e}"
            print(f"[MongoDB] ConfigurationError: {e}")
            logger.error("MongoDB configuration error: %s", e)
        except pymongo.errors.PyMongoError as e:
            self.error = f"MongoDB error: {e}"
            print(f"[MongoDB] {type(e).__name__}: {e}")
            logger.error("Unexpected MongoDB error (%s): %s", type(e).__name__, e, exc_info=True)

    def save_raw_result(self, text):
        """ Normally this would save the raw result to a json object.
        In this case, the MongoClient is already returning a JSON object."""

    def fill_search_result_meta_data(self):
        """Fills the search result metadata. In the download_result method, the raw result is created and the
        total number of documents is retrieved. The page number is also set in the download_result method."""

        # Check if this is a single document query (raw_result is the document itself)
        if "total" in self.raw_result:
            self.total = self.raw_result["total"]
        elif self.query.get('type') == 'single':
            # Single document query - check if document exists
            self.total = 1 if self.raw_result else 0
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
        elif self.query.get('type') == 'single' and self.raw_result:
            # Single document query - wrap in list
            self.results = [self.raw_result]

    def get_id_value(self, result):
        """ Overwrite the default get_id_value method to get the id from the result. """
        return get_nested_value(result, self.search_configuration.search_id_field)
