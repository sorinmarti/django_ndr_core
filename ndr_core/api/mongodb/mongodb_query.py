from ndr_core.models import NdrCoreSearchField
from ndr_core.api.base_query import BaseQuery


class MongoDBQuery(BaseQuery):

    def get_simple_query(self, search_term, add_page_and_size=True):
        """ Not Implemented """
        query = {
            'transcription.original': {
                '$regex': 'ersuchet',
                '$options': 'i'
            },
            'date.ref': {
                '$gte': '1729-01-03',
                '$lte': '1729-01-05'
            },
            'tags.tags': {
                '$all': [
                    'notice'
                ]
            },
            'type.id': 'curious',
            'type.language': 'de',
            'source.issue': 1
        }
        return query
        #return {"transcription.original": {"$regex": search_term, "$options": "i"}}

    def get_advanced_query(self, *kwargs):
        print("ADVANCED")
        query = {}
        for field_name in self.values:
            try:
                field = NdrCoreSearchField.objects.get(field_name=field_name)
                value = None

                if field.field_type == NdrCoreSearchField.FieldType.STRING:
                    if self.values[field_name] != '':
                        value = {"$regex": self.values[field_name], "$options": "i"}
                if field.field_type == NdrCoreSearchField.FieldType.MULTI_LIST:
                    print(self.values[field_name])
                    if type(self.values[field_name]) == list and len(self.values[field_name]) > 0:
                        value = {"$all": self.values[field_name]}

                if value is not None:
                    query[field.api_parameter] = value
            except NdrCoreSearchField.DoesNotExist:
                pass

        print(query)

        query = {
            'transcription.original': {
                '$regex': 'ersuchet',
                '$options': 'i'
            },
            'date.ref': {
                '$gte': '1729-01-03',
                '$lte': '1729-01-05'
            },
            'tags.tags': {
                '$all': [
                    'notice'
                ]
            },
            'type.id': 'curious',
            'type.language': 'de',
            'source.issue': 1
        }
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
        self.values[field_name] = value
