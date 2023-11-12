"""The base query class provides basic functionality to compose an
API query based on an API Configuration. It is an abstract base class
which has abstract methods which need to be overwritten for an actual
implementation."""
from abc import ABC, abstractmethod


class BaseQuery(ABC):
    """The base query class provides basic functionality to compose an
    API query based on an API Configuration. """

    Q_SIMPLE = 'SIMPLE'
    Q_ADVANCED = 'ADVANCED'
    Q_LIST = 'LIST'

    search_config = None
    page = 1

    def __init__(self, search_configuration, page=1):
        self.search_config = search_configuration
        self.page = page

        self.values = {}
        self.search_term = ''

    @abstractmethod
    def get_simple_query(self, search_term, add_page_and_size=True, and_or='and'):
        """Returns a query to retrieve a list of records."""

    @abstractmethod
    def get_advanced_query(self, *kwargs):
        """Returns a query to retrieve a list of records."""

    @abstractmethod
    def get_list_query(self, list_name, add_page_and_size=True, search_term=None, tags=None):
        """Returns a query to retrieve a list of records."""

    @abstractmethod
    def get_record_query(self, record_id):
        """Returns a query to retrieve a single record."""

    @abstractmethod
    def get_explain_query(self, search_type):
        """Returns a query to explain the search."""

    def get_base_string(self):
        """ Composes the base string for the API. Example https://api-host.com:80/query/ """
        return self.search_config.api_connection_url

    def set_value(self, field_name, value):
        """Sets a value=key setting to compose a query from"""
        self.values[field_name] = value
