from ndr_core.api.ndr_core.ndr_core_query import NdrCoreQuery
from ndr_core.api.ndr_core.ndr_core_result import NdrCoreResult


class ApiFactory:
    """TODO """

    def __init__(self, api_configuration):
        self.api_configuration = api_configuration

    def get_query_class(self):
        if self.api_configuration.api_type.name == "ndr_core":
            return NdrCoreQuery
        return None

    def get_result_class(self):
        if self.api_configuration.api_type.name == "ndr_core":
            return NdrCoreResult
        return None
