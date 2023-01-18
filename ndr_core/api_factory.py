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

    def __init__(self, api_configuration):
        self.api_configuration = api_configuration

    def get_query_class(self):
        if self.api_configuration.api_type.name == "ndr_core":
            return NdrCoreQuery
        elif self.api_configuration.api_type.name == "api_ninjas":
            return ApiNinjasQuery
        elif self.api_configuration.api_type.name == "mongodb":
            return MongoDBQuery
        elif self.api_configuration.api_type.name == "ddb":
            return DDBQuery
        print("API IMPLEMENTATION NOT FOUND")
        return None

    def get_result_class(self):
        if self.api_configuration.api_type.name == "ndr_core":
            return NdrCoreResult
        elif self.api_configuration.api_type.name == "api_ninjas":
            return ApiNinjasResult
        elif self.api_configuration.api_type.name == "mongodb":
            return MongoDBResult
        elif self.api_configuration.api_type.name == "ddb":
            return DDBResult
        print("API IMPLEMENTATION NOT FOUND")
        return None
