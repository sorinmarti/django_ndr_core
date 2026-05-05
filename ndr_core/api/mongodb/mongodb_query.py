"""Implementation of the mongo DB API. """
from ndr_core.models import NdrCoreSearchField
from ndr_core.api.base_query import BaseQuery


class MongoDBQuery(BaseQuery):
    """Implementation of the mongo DB API. """

    def get_simple_query(self, search_term, add_page_and_size=True, and_or='and'):
        """Returns a simple search query. Uses Atlas Search when enabled, otherwise falls back to regex."""

        # Convert sort_order to MongoDB format: 1 for ascending, -1 for descending
        sort_direction = -1 if self.search_config.sort_order == 'desc' else 1

        mongodb_settings = (self.search_config.api_settings or {}).get('mongodb', {})
        if mongodb_settings.get('use_atlas_search', False):
            return self._build_atlas_search_query(search_term, sort_direction)

        search_words = search_term.split(' ')
        if and_or == 'and':
            regex_string = '^(?=.*' + ')(?=.*'.join(search_words) + ')'
        else:
            regex_string = f"({'|'.join(search_words)})"

        regex_clause = {'$regex': regex_string, '$options': 'msi'}

        path_parts = [p.strip() for p in self.search_config.simple_query_main_field.split(',') if p.strip()]
        if len(path_parts) > 1:
            field_filter = {'$or': [{field: regex_clause} for field in path_parts]}
        else:
            field_filter = {path_parts[0]: regex_clause}

        query = {
            'filter': field_filter,
            'sort': list({self.search_config.sort_field: sort_direction}.items()),
            'page': int(self.page)
        }
        return query

    def _build_atlas_search_query(self, search_term, sort_direction):
        """Builds a MongoDB Atlas Search aggregation pipeline query.

        Reads settings from api_settings['mongodb']:
          atlas_search_index           str   index name (default: 'default')
          atlas_search_fuzzy           bool  enable fuzzy matching
          atlas_search_fuzzy_max_edits int   max Levenshtein edits (1 or 2)
          atlas_sort_by_relevance      bool  sort by score (default True);
                                            False uses sort_field/sort_order
          atlas_highlighting           bool  inject _hl highlights into results

        The search path comes from simple_query_main_field (comma-separated for
        multi-field, e.g. "actor.entity_canonical,content.raw_text").
        """
        mongodb_settings = (self.search_config.api_settings or {}).get('mongodb', {})

        index_name = mongodb_settings.get('atlas_search_index') or 'default'
        use_fuzzy = mongodb_settings.get('atlas_search_fuzzy', False)
        max_edits = mongodb_settings.get('atlas_search_fuzzy_max_edits') or 1
        sort_by_relevance = mongodb_settings.get('atlas_sort_by_relevance', True)
        use_highlighting = mongodb_settings.get('atlas_highlighting', False)
        page = int(self.page)
        page_size = self.search_config.page_size
        skip = page * page_size - page_size

        # simple_query_main_field doubles as the search path; supports comma-sep multi-field
        raw_path = self.search_config.simple_query_main_field or '_search'
        path_parts = [p.strip() for p in raw_path.split(',') if p.strip()]
        path = path_parts[0] if len(path_parts) == 1 else path_parts

        # autocomplete_path is a single field indexed with type:autocomplete in Atlas.
        # When set, the query becomes a compound that combines full-token text matching
        # with prefix (edge-gram) matching, so partial input like "aebi" finds "Aebischer".
        autocomplete_path = (mongodb_settings.get('atlas_autocomplete_path') or '').strip()

        text_clause = {"query": search_term, "path": path}
        if use_fuzzy:
            text_clause["fuzzy"] = {"maxEdits": max_edits}

        if autocomplete_path:
            # compound: text covers all paths (full-token + fuzzy),
            # autocomplete covers prefix matching on the autocomplete-indexed field.
            operator = {
                "compound": {
                    "should": [
                        {"text": text_clause},
                        {"autocomplete": {"query": search_term, "path": autocomplete_path}},
                    ],
                    "minimumShouldMatch": 1,
                }
            }
        else:
            operator = {"text": text_clause}

        search_stage = {"index": index_name, **operator}
        if use_highlighting:
            search_stage["highlight"] = {"path": path_parts}

        pipeline = [{"$search": search_stage}]

        if not sort_by_relevance:
            pipeline.append({"$sort": {self.search_config.sort_field: sort_direction}})

        if use_highlighting:
            # Materialize the $searchHighlights metadata field into a regular document field
            # before $facet, which strips metadata fields from its sub-pipeline documents.
            pipeline.append({"$addFields": {"_searchHighlights": {"$meta": "searchHighlights"}}})

        pipeline.append({"$facet": {
            "hits": [
                {"$skip": skip},
                {"$limit": page_size}
            ],
            "total": [{"$count": "count"}]
        }})

        return {
            'pipeline': pipeline,
            'sort': list({self.search_config.sort_field: sort_direction}.items()),
            'page': page,
            'type': 'atlas_search'
        }

    def get_advanced_query(self, *kwargs):
        # Convert sort_order to MongoDB format: 1 for ascending, -1 for descending
        sort_direction = -1 if self.search_config.sort_order == 'desc' else 1

        query = {
            'filter': {},
            'sort': list({self.search_config.sort_field: sort_direction}.items()),
            'page': int(self.page)
        }

        and_list = []
        or_list = []
        for field in self.get_field_configurations():
            # print("FIELD", field.parameter, field.condition, field.value)

            value = None
            if field.field_type == 'string':
                # Handle string comparison operators
                if field.operator == 'contains':
                    value = {"$regex": field.value, "$options": "i"}
                elif field.operator == '=':
                    value = field.value
                elif field.operator == '!=':
                    value = {"$ne": field.value}
                else:
                    # Default to regex for backwards compatibility
                    value = {"$regex": field.value, "$options": "i"}
            elif field.field_type == 'number':
                # Handle number comparison operators
                if field.operator == '=':
                    value = field.value
                elif field.operator == '>':
                    value = {"$gt": field.value}
                elif field.operator == '<':
                    value = {"$lt": field.value}
                elif field.operator == '>=':
                    value = {"$gte": field.value}
                elif field.operator == '<=':
                    value = {"$lte": field.value}
                elif field.operator == '!=':
                    value = {"$ne": field.value}
                else:
                    value = field.value
            elif field.field_type == 'float':
                # Handle float comparison operators
                if field.operator == '=':
                    value = field.value
                elif field.operator == '>':
                    value = {"$gt": field.value}
                elif field.operator == '<':
                    value = {"$lt": field.value}
                elif field.operator == '>=':
                    value = {"$gte": field.value}
                elif field.operator == '<=':
                    value = {"$lte": field.value}
                elif field.operator == '!=':
                    value = {"$ne": field.value}
                else:
                    value = field.value
            elif field.field_type == 'number_range':
                if isinstance(field.value, str):
                    value = {"$regex": field.value}
                else:
                    value = {"$in": field.value}
            elif field.field_type == 'date':
                # Handle date comparison operators
                if field.operator == '=':
                    value = field.value
                elif field.operator == '>':
                    value = {"$gt": field.value}
                elif field.operator == '<':
                    value = {"$lt": field.value}
                elif field.operator == '>=':
                    value = {"$gte": field.value}
                elif field.operator == '<=':
                    value = {"$lte": field.value}
                else:
                    value = field.value
            elif field.field_type == 'list':
                value = field.value
            elif field.field_type == 'multi_list':
                if field.condition == 'or':
                    value = {"$in": field.value}
                else:
                    value = {"$all": field.value}
            elif field.field_type == 'boolean':
                # Handle boolean comparison operators
                if field.operator == '=':
                    value = field.value
                elif field.operator == '!=':
                    value = {"$ne": field.value}
                else:
                    value = field.value
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

        return query

    def get_list_query(self, list_name, add_page_and_size=True, search_term=None, tags=None):
        """ Not Implemented """
        return None

    def get_record_query(self, record_id):
        """ Single record query by id """
        record_query = {'filter': {self.search_config.search_id_field: record_id}, 'type': 'single'}
        return record_query

    def get_all_items_query(self, add_page_and_size=True):
        """Returns a query to retrieve all items without filters."""
        # Convert sort_order to MongoDB format: 1 for ascending, -1 for descending
        sort_direction = -1 if self.search_config.sort_order == 'desc' else 1

        query = {
            'filter': {},  # Empty filter returns all documents
            'sort': list({self.search_config.sort_field: sort_direction}.items()),
            'page': int(self.page)
        }
        return query

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
