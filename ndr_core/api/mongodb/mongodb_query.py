from ndr_core.models import NdrCoreSearchField
from ndr_core.api.base_query import BaseQuery

# TODO
# - The simple query field name is hardcoded to 'transcription.original'
# - The id field name is hardcoded to 'source.selector.id'
# - The sort field name is hardcoded to 'date.ref' and the sort order is hardcoded to 1 (ascending)
# The above should be configurable in the API configuration

class MongoDBQuery(BaseQuery):

    def get_simple_query(self, search_term, add_page_and_size=True):
        """ Not Implemented """
        query = {
            'filter': {
                '$or': [
                    {'transcription.original': {
                        '$regex': search_term,
                        '$options': 'i'
                    }},
                    {'transcription.corrected': {
                        '$regex': search_term,
                        '$options': 'i'
                    }}
                ]
            },
            'sort': list({'date.ref': 1}.items()),
            'page': int(self.page)
        }
        return query

    def get_advanced_query(self, *kwargs):
        query = {
            'filter': {},
            'sort': list({'date.ref': 1}.items()),
            'page': int(self.page)
        }

        for field_name in self.values:
            try:
                field = NdrCoreSearchField.objects.get(field_name=field_name)
                value = None

                if field.field_type == NdrCoreSearchField.FieldType.STRING:
                    if self.values[field_name] != '':
                        value = {"$regex": self.values[field_name], "$options": "i"}
                elif field.field_type == NdrCoreSearchField.FieldType.NUMBER:
                    value = self.values[field_name]
                elif field.field_type == NdrCoreSearchField.FieldType.LIST:
                    if self.values[field_name] != '':
                        value = self.values[field_name]
                elif field.field_type == NdrCoreSearchField.FieldType.MULTI_LIST:
                    print(self.values[field_name])
                    if type(self.values[field_name]) == list and len(self.values[field_name]) > 0:
                        # TODO - This should be configurable
                        value = {"$all": self.values[field_name]}
                        # value = {"$in": self.values[field_name]}
                elif field.field_type == NdrCoreSearchField.FieldType.DATE:
                    # TODO: Implement
                    pass
                elif field.field_type == NdrCoreSearchField.FieldType.DATE_RANGE:
                    if self.values[field_name][0] is not None and self.values[field_name][1] is not None:
                        date_from = self.values[field_name][0].strftime('%Y-%m-%d')
                        date_to = self.values[field_name][1].strftime('%Y-%m-%d')
                        value = {"$gte": date_from, "$lte": date_to}
                elif field.field_type == NdrCoreSearchField.FieldType.NUMBER_RANGE:
                    pass

                if value is not None:
                    query['filter'][field.api_parameter] = value
            except NdrCoreSearchField.DoesNotExist:
                pass

        return query

    def get_list_query(self, list_name, add_page_and_size=True, search_term=None, tags=None):
        """ Not Implemented """
        return None

    def get_record_query(self, record_id):
        """ Not Implemented """
        record_query = {'filter': {"source.selector.id": record_id}, 'type': 'single'}
        return record_query

    def get_explain_query(self, search_type):
        """ Not Implemented """
        return None

    def set_value(self, field_name, value):
        """Sets a value=key setting to compose a query from"""
        self.values[field_name] = value
