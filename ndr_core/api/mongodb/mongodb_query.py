from ndr_core.models import NdrCoreSearchField
from ndr_core.api.base_query import BaseQuery


class MongoDBQuery(BaseQuery):

    def get_simple_query(self, search_term, add_page_and_size=True):
        """ Not Implemented """
        return {"transcription.original": {"$regex": search_term, "$options": "i"}}

    def get_advanced_query(self, *kwargs):
        print("ADVANCED")
        query = {}
        for val in self.values:
            query['name.transcription'] = self.values[val]
            print(val, self.values[val], query)
        return query

    def get_list_query(self, list_name, add_page_and_size=True, search_term=None, tags=None):
        """ Not Implemented """
        return None

    def get_record_query(self, record_id):
        """ Not Implemented """
        record_query = {"id": record_id}
        return record_query

    def get_explain_query(self, search_type):
        """ Not Implemented """
        return None

    def set_value(self, field_name, value):
        """Sets a value=key setting to compose a query from"""
        field = NdrCoreSearchField.objects.filter(field_name=field_name).first()
        if field is not None:
            if field.field_type == NdrCoreSearchField.FieldType.STRING:
                value = {"$regex": value, "$options": "i"}
            if field.field_type == NdrCoreSearchField.FieldType.LIST:
                print("LIST")
        else:
            value = {"$regex": value, "$options": "i"}
        self.values[field_name] = value
