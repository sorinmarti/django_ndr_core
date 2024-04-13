"""Implementation of the mongo DB API. """
from ndr_core.models import NdrCoreSearchField
from ndr_core.api.base_query import BaseQuery


class MongoDBQuery(BaseQuery):
    """Implementation of the mongo DB API. """

    def get_simple_query(self, search_term, add_page_and_size=True, and_or='and'):
        """ Not Implemented """

        search_words = search_term.split(' ')
        if and_or == 'and':
            regex_string = '^(?=.*' + ')(?=.*'.join(search_words) + ')'
        else:
            regex_string = f"({'|'.join(search_words)})"

        query = {
            'filter': {
                self.search_config.simple_query_main_field: {
                    '$regex': regex_string,
                    '$options': 'msi'
                }
            },
            'sort': list({self.search_config.sort_field: 1}.items()),
            'page': int(self.page)
        }
        return query

    def get_advanced_query(self, *kwargs):
        query = {
            'filter': {},
            'sort': list({self.search_config.sort_field: 1}.items()),
            'page': int(self.page)
        }

        and_list = []
        or_list = []
        for field in self.get_field_configurations():
            # print("FIELD", field.parameter, field.condition, field.value)

            value = None
            if field.field_type == 'string':
                value = {"$regex": field.value, "$options": "i"}
            elif field.field_type == 'number':
                value = field.value
            elif field.field_type == 'number_range':
                if isinstance(field.value, str):
                    value = {"$regex": field.value}
                else:
                    value = {"$in": field.value}
            elif field.field_type == 'list':
                value = field.value
            elif field.field_type == 'multi_list':
                if field.condition == 'or':
                    value = {"$in": field.value}
                else:
                    value = {"$all": field.value}
            elif field.field_type == 'boolean':
                value = {'$eq': field.value}
            elif field.field_type == 'boolean_list':
                for key, condition in field.value:
                    if field.condition == 'or':
                        or_list.append({key: condition})
                    else:
                        and_list.append({key: condition})

            if value is not None:
                query['filter'][field.parameter] = value

        if len(and_list) > 0:
            query['filter']['$and'] = and_list
        if len(or_list) > 0:
            query['filter']['$or'] = or_list

        """
        elif field.field_type == NdrCoreSearchField.FieldType.DATE_RANGE:
            if self.values[field_name][0] is not None and self.values[field_name][1] is not None:
                date_from = self.values[field_name][0].strftime('%Y-%m-%d')
                date_to = self.values[field_name][1].strftime('%Y-%m-%d')
                value = {"$gte": date_from, "$lte": date_to}"""

        #print(query)
        return query

    def get_list_query(self, list_name, add_page_and_size=True, search_term=None, tags=None):
        """ Not Implemented """
        return None

    def get_record_query(self, record_id):
        """ Not Implemented """
        record_query = {'filter': {self.search_config.search_id_field: record_id}, 'type': 'single'}
        return record_query

    def get_explain_query(self, search_type):
        """ Not Implemented """
        return None

    def set_value(self, field_name, value):
        """Sets a value=key setting to compose a query from"""
        self.values[field_name] = value

    @staticmethod
    def get_value_conf(item_value):
        """Gets the value of a key setting"""
        if "__" in item_value:
            split = item_value.split('__')
            return split[0], True if split[1] == 'true' else False

        return item_value, True
