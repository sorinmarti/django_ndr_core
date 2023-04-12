"""The base query class provides basic functionality to compose an API query based on an API Configuration.
It is an abstract base class which has abstract methods which need to be overwritten for an actual implementation."""
from abc import ABC, abstractmethod


class BaseQuery(ABC):
    """TODO """

    Q_SIMPLE = 'SIMPLE'
    Q_ADVANCED = 'ADVANCED'
    Q_LIST = 'LIST'

    api_config = None
    search_config = None
    page = 1

    def __init__(self, search_configuration, page=1):
        self.search_config = search_configuration
        self.api_config = self.search_config.api_configuration
        self.page = page

        self.values = {}
        self.search_term = ''

    @abstractmethod
    def get_simple_query(self, search_term, add_page_and_size=True):
        pass

    @abstractmethod
    def get_advanced_query(self, *kwargs):
        pass

    @abstractmethod
    def get_list_query(self, list_name, add_page_and_size=True, search_term=None, tags=None):
        pass

    @abstractmethod
    def get_record_query(self, record_id):
        pass

    @abstractmethod
    def get_explain_query(self, search_type):
        pass

    def get_base_string(self, show_port=True):
        """ Composes the base string for the API. Example https://api-host.com:80/query/ """

        base_string = f"{self.api_config.Protocol(self.api_config.api_protocol).label}://{self.api_config.api_host}"
        if show_port:
            base_string += f":{self.api_config.api_port}"
        base_string += "/"
        if self.api_config.api_url_stub is not None:
            base_string += f'{self.api_config.api_url_stub}'

        return base_string

    def set_value(self, field_name, value):
        """Sets a value=key setting to compose a query from"""
        self.values[field_name] = value
