from ndr_core.api.base_query import BaseQuery
from ndr_core.models import NdrCoreSearchField


class NdrCoreQuery(BaseQuery):
    """TODO """

    def __init__(self, api_configuration, page=1):
        super().__init__(api_configuration, page)

    def get_simple_query(self, search_term, add_page_and_size=True):
        self.search_term = search_term
        query = self.get_ndr_base_string("basic", add_page_and_size=add_page_and_size)
        if add_page_and_size:
            query += f"&t={search_term}"
        else:
            query += f"?t={search_term}"
        return query

    def get_advanced_query(self, add_page_and_size=True):
        query = self.get_ndr_base_string("advanced", add_page_and_size=add_page_and_size)
        if add_page_and_size:
            param_divider = '&'
        else:
            param_divider = '?'

        for field_name in self.values:
            field = NdrCoreSearchField.objects.get(field_name=field_name)
            query += f"{param_divider}{field.api_parameter}={self.values[field_name]}"
            param_divider = '&'
        return query

    def get_list_query(self, list_name, add_page_and_size=True, search_term=None, tags=None):
        self.search_term = search_term
        query = self.get_ndr_base_string("list", add_page_and_size=add_page_and_size)

        if add_page_and_size:
            query += f"&l={list_name}"
        else:
            query += f"?l={list_name}"

        if search_term is not None:
            query += f"&t={search_term}"
        if tags is not None:
            if type(tags) == str:
                query += f"&tags={tags}"
            if type(tags) == list:
                query += f"&tags={','.join(tags)}"
        return query

    def get_record_query(self, record_id):
        query = self.get_ndr_base_string("fulldata", add_page_and_size=False)
        query += f"?id={record_id}"
        return query

    def get_explain_query(self, search_type):
        if search_type == BaseQuery.Q_SIMPLE:
            query = self.get_simple_query(self.search_term, add_page_and_size=False)
            query.replace('query/basic', 'query/basic_explain')
        elif search_type == BaseQuery.Q_ADVANCED:
            query = self.get_advanced_query(add_page_and_size=False)
            query.replace('query/advanced', 'query/advanced_explain')
        elif search_type == BaseQuery.Q_LIST:
            query = self.get_advanced_query(add_page_and_size=False)
            query.replace('query/list', 'query/list_explain')
        else:
            raise ValueError('search_type must be one of SIMPLE, ADVANCED, LIST')
        return query

    def get_ndr_base_string(self, query_type, add_page_and_size=True):
        """ Composes the base string for the API. Example https://api-host.com:80/query/<type>?s=10&p=1
            (This requests the first 10 results: page=1, size=10)"""
        base_string = self.get_base_string()
        base_string += f'query/{query_type}'

        if add_page_and_size:
            base_string += f"?s={self.api_config.api_page_size}&p={self.page}"
        return base_string
