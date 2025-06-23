from ndr_core.api.base_query import BaseQuery


class SimpleAttrsQuery(BaseQuery):

    def get_simple_query(self, search_term, add_page_and_size=True, and_or='and'):
        pass

    def get_advanced_query(self, *kwargs):
        pass

    def get_list_query(self, list_name, add_page_and_size=True, search_term=None, tags=None):
        pass

    def get_record_query(self, record_id):
        pass

    def get_explain_query(self, search_type):
        pass
