""" Simple implementation of the ninja-api API. """
from ndr_core.api.base_query import BaseQuery


class ApiNinjasQuery(BaseQuery):
    """Simple implementation of the ninja-api API. """

    def get_simple_query(self, search_term, add_page_and_size=True, and_or='and'):
        return self.get_base_string() + "?name=" + search_term

    def get_advanced_query(self, *kwargs):
        query = self.get_base_string() + "?"
        for field_value in self.values:
            query += f"{field_value}={self.values[field_value]}"
        return query

    def get_list_query(self, list_name, add_page_and_size=True, search_term=None, tags=None):
        """ Not Implemented """
        return None

    def get_record_query(self, record_id):
        """ Not Implemented """
        return None

    def get_explain_query(self, search_type):
        """ Not Implemented """
        return None
