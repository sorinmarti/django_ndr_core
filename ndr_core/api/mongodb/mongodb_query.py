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

        for field_name in self.values:
            print("FIELD", field_name, self.values[field_name])
            try:
                field = NdrCoreSearchField.objects.get(field_name=field_name)
                value = None
                filter_name = field.api_parameter

                # STRING:
                if field.field_type == NdrCoreSearchField.FieldType.STRING:
                    if self.values[field_name] != '':
                        value = {"$regex": self.values[field_name], "$options": "i"}
                elif field.field_type == NdrCoreSearchField.FieldType.NUMBER:
                    value = self.values[field_name]
                elif field.field_type == NdrCoreSearchField.FieldType.NUMBER_RANGE:
                    if len(self.values[field_name]) > 0:
                        if field.data_field_type == "int":
                            value = {'$in': self.values[field_name]}
                        else:
                            regex_string = f'({"|".join(map(str, self.values[field_name]))})'
                            if field.input_transformation_regex is not None and field.input_transformation_regex != '':
                                if '{_value_}' in field.input_transformation_regex:
                                    regex_string = field.input_transformation_regex.replace('{_value_}', regex_string)
                            value = {'$regex': regex_string}
                # LIST:
                elif field.field_type == NdrCoreSearchField.FieldType.LIST:
                    if self.values[field_name] != '':
                        key, condition = self.get_value_conf(self.values[field_name])
                        value = key
                # MULTI_LIST:
                elif field.field_type == NdrCoreSearchField.FieldType.MULTI_LIST:
                    if type(self.values[field_name]) == list and len(self.values[field_name]) > 0:
                        # TODO - This should be configurable
                        items = []
                        for item in self.values[field_name]:
                            key, condition = self.get_value_conf(item)
                            items.append(key)

                        value = {"$all": items}
                        # value = {"$in": self.values[field_name]}
                # BOOLEAN_LIST:
                elif field.field_type == NdrCoreSearchField.FieldType.BOOLEAN_LIST:
                    filter_name = '$or'
                    value = []
                    for item in self.values[field_name]:
                        key, condition = self.get_value_conf(item)
                        value.append({key: {"$eq": condition}})

                elif field.field_type == NdrCoreSearchField.FieldType.DATE:
                    pass
                elif field.field_type == NdrCoreSearchField.FieldType.DATE_RANGE:
                    if self.values[field_name][0] is not None and self.values[field_name][1] is not None:
                        date_from = self.values[field_name][0].strftime('%Y-%m-%d')
                        date_to = self.values[field_name][1].strftime('%Y-%m-%d')
                        value = {"$gte": date_from, "$lte": date_to}
                elif field.field_type == NdrCoreSearchField.FieldType.BOOLEAN:
                    value = {'$eq': self.values[field_name]}

                if value is not None:
                    if filter_name in query['filter']:
                        query['filter'][filter_name] = query['filter'][filter_name] + value
                    else:
                        query['filter'][filter_name] = value
            except NdrCoreSearchField.DoesNotExist:
                pass

        print(query)
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
