from ndr_core.api.mongodb.mongodb_query import MongoDBQuery
from ndr_core.api.mongodb.mongodb_result import MongoDBResult
from ndr_core.api.api_ninjas.api_ninjas_query import ApiNinjasQuery
from ndr_core.api.api_ninjas.api_ninjas_result import ApiNinjasResult
from ndr_core.api.ndr_core.ndr_core_query import NdrCoreQuery
from ndr_core.api.ndr_core.ndr_core_result import NdrCoreResult
from ndr_core.api.ddb_api.ddb_query import DDBQuery
from ndr_core.api.ddb_api.ddb_result import DDBResult


class ApiFactory:
    """The API factory returns Query and Result classes for a selected API implementation. """

    api_mapping = {
        "ndr_core": {"query": NdrCoreQuery, "result": NdrCoreResult},
        "api_ninjas": {"query": ApiNinjasQuery, "result": ApiNinjasResult},
        "mongodb": {"query": MongoDBQuery, "result": MongoDBResult},
        "ddb": {"query": DDBQuery, "result": DDBResult}
    }

    def __init__(self, api_configuration):
        self.api_configuration = api_configuration

    def get_query_class(self):
        """Returns the query class for the selected API implementation."""
        if self.api_configuration.api_type.name in self.api_mapping:
            return self.api_mapping[self.api_configuration.api_type.name]["query"]
        else:
            raise Exception("API IMPLEMENTATION NOT FOUND")

    def get_result_class(self):
        """Returns the result class for the selected API implementation."""
        if self.api_configuration.api_type.name in self.api_mapping:
            return self.api_mapping[self.api_configuration.api_type.name]["result"]
        else:
            raise Exception("API IMPLEMENTATION NOT FOUND")
