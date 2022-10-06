from ndr_core.models import SearchConfiguration, NdrSearchField


class Query:

    api_config = None

    def __init__(self, config_name):
        config = SearchConfiguration.objects.get(api_configuration__api_name=config_name)
        self.api_config = config.api_configuration

        self.values = {}

    def get_basic_query(self, search_term, page):
        query = self.get_base_string("basic", page)
        query += f"&t={search_term}"
        return query

    def get_advanced_query(self, page):
        query = self.get_base_string("advanced", page)
        for field_name in self.values:
            field = NdrSearchField.objects.get(field_name=field_name)
            query += f"&{field.api_parameter}={self.values[field_name]}"
        return query

    def get_base_string(self, query_type, page):
        """ Composes the base string for the API endpoint. Example https://api-host.com:80/endpoint/?s=10&p=1
            (This requests the first 10 results: page=1, size=10)"""

        base_string = f"{self.api_config.Protocol(self.api_config.api_protocol).label}://{self.api_config.api_host}:" \
                      f"{self.api_config.api_port}/query/{query_type}"
        if page != 0:
            base_string += f"?s={self.api_config.api_page_size}&p={page}"
        return base_string

    def set_value(self, field_name, value):
        self.values[field_name] = value
