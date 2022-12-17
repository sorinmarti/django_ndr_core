from abc import ABC, abstractmethod

from ndr_core.geo_ip_utils import get_user_ip, get_geolocation
from ndr_core.models import NdrCoreValue, NdrCoreSearchStatisticEntry


class BaseQuery(ABC):
    """TODO """

    Q_SIMPLE = 'SIMPLE'
    Q_ADVANCED = 'ADVANCED'
    Q_LIST = 'LIST'

    api_config = None
    page = 1

    def __init__(self, api_configuration, page=1):
        self.api_config = api_configuration
        self.page = page

        self.values = {}
        self.search_term = ''

    @abstractmethod
    def get_simple_query(self, search_term, add_page_and_size=True):
        pass

    @abstractmethod
    def get_advanced_query(self, add_page_and_size=True):
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

    def get_base_string(self):
        """ Composes the base string for the API. Example https://api-host.com:80/query/ """

        base_string = f"{self.api_config.Protocol(self.api_config.api_protocol).label}://{self.api_config.api_host}:" \
                      f"{self.api_config.api_port}/"
        if self.api_config.api_url_stub is not None:
            base_string += f'{self.api_config.api_url_stub}/'

        return base_string

    def set_value(self, field_name, value):
        self.values[field_name] = value

    def log_search(self, request, search_term):
        if NdrCoreValue.get_or_initialize('statistics_feature').get_value():
            ip = get_user_ip(request)
            location = get_geolocation(ip)

            NdrCoreSearchStatisticEntry.objects.create(search_api=self.api_config,
                                                       search_term=search_term,
                                                       search_location=location)  # TODO
