Creating your own API Implementation
====================================
The first class is the **BaseQuery** class, the second one is the **BaseResult** class. The
first one is used to compose an API query; the second one is used to request the query
at the API endpoint, parse the result and format it so it can be used by NDR Core. Both
classes are Abstract classes and need to be implemented to program a new API. The
following steps are necessary to implement a new API:

- Clone NDR Core from GitHub and create a new branch.
- Decide on a name for the API implementation. It needs to be a valid directory name.
- Create a new folder for the API implementation in the ndr_core/api/ folder.
- Create two Python files in the new folder: ``<apiname>_query.py`` and ``<apiname>_result.py``.
- In each file, create a class with the name ``<ApiName>Query`` and ``<ApiName>Result`` respectively.
- Make the classes inherit from the ``BaseQuery`` and ``BaseResult`` classes.
- Implement the abstract methods of the classes.
- Add your implementation the NDR Core’s fixtures.
- Add your implementation to the ``ndr_core/api_factory.py`` file.

Overriding Abstract Base Classes
--------------------------------
The first class to be implemented is the BaseQuery class. The class is initialized
with the search configuration and the page to display. It needs to implement a
number of methods which are called by the system to query an API. NDR Core paginates
results which means that only the number defined as "page size" in the search
configuration are displayed on a page. Therefore a page number is needed to query the API for
the correct results. This mechanism is absolutely necessary because loading potentially
thousands of results would not work in the front end and is not supported by most APIs
anyway. The methods to implement are ``get_simple_query`` (1), ``get_advanced_query``
(2), ``get_list_query`` (3), ``get_record_query`` (4) and ``get_explain_query`` (5).

::

    class BaseQuery (ABC):

        def __init__(self, search_config, page ):
            [...]

        @abstractmethod
        def get_simple_query(self, search_term, and_or ='and'):
            pass

        @abstractmethod
        def get_advanced_query(self, *kwargs):
            pass

        @abstractmethod
        def get_list_query(self, list_name, search_term):
            pass

        @abstractmethod
        def get_record_query(self, record_id):
            pass

        @abstractmethod
        def get_explain_query(self, search_type):
            pass

        def get_base_string( self ):
            [...]

        def set_value(self, field_name, value ):
            [...]


The simple query (1) means the one-field-catches-all search, it takes exactly one
search term and returns all results which match the search term. Additionally a search
can be done with the “AND” or “OR” modifier (AND is the default). If the search term
contains spaces it is split up and either queried as a list of search terms (OR) or as a
single search term (AND). The advanced query (2) is used to query specific fields with
specific values. The search form sends all values to the API query class and the class
has to compose a query string from the values. The list query (3) is used to query a
curated list of values. This functionality is planned but not yet implemented in NDR
Core. The idea is to have curated lists at an API endpoint (meaning a subset of the data)
which can be queried to create case study presentations or similar elements. Instead of
querying the whole database, the user can filter down a curated list which is shown on
a page talking about a specific aspect of the data. The record query (4) is used to query a
single record. An ID field has to be configured in the search configuration which is used
to query a single record in the database. This is used to reference and download single results. The explain query (5) is another functionality which is planned but not yet
implemented. The idea is that an API can provide an explanation of the search result,
for example a list of all years the result contains. This would allow for filtering down
the data after a result set has been found. The other methods (here marked with [...])
are implemented in the base class and are generic enough that they do not need to be
implemented in the API implementation.

The second class to be implemented is the BaseResult class. The class is initialized
with the search configuration, the query and the request. It needs to implement a number of methods
which are called by the system to query an API, load the result and return it. The methods to
implement are ``save_raw_result`` (1), ``fill_search_result_meta_data`` (2), ``fill_results`` (3)

::

    class BaseResult (ABC):
        def __init__ (self , search_config , query , request ):
            [...]

        @abstractmethod
        def save_raw_result (self , raw_result ):
            pass

        @abstractmethod
        def fill_search_result_meta_data (self , search_result ):
            pass

        @abstractmethod
        def fill_results (self , search_result ):
            pass

        def download_result ( self ):
            [...]

        # Various other methods
        [...]


As one can see, the class is initialized with the search configuration, the query and
the request. The query is an object of the query class implementation and the request is
the Django request object. Because the base implementation is able to send the request
and download the result based on the information from the query object, the only work
to do to save the raw result (1) is to convert it into Python list with any data inside. The
fill meta data (2) method is used to provide basic information about the page, the page
size, the number of pages and the total number of results. Finally, the fill results (3)
method is used to convert the raw result into a list of result objects. A lot of APIs return
JSON results which can be converted into a Python list of dictionaries with very little
effort. But also if the result is an XML or CSV string, it can be converted into a Python
list of dictionaries.

After implementing these two classes, NDR Core needs to be told about it, by creating a
database object to select in the administration interface. This is done by adding the
API implementation to the fixtures of NDR Core or by entering your values directly in
your installation database. It is recommended to add the implementation to the fixtures
of NDR Core so you can create a pull request and add your implementation to the main
branch of NDR Core. Refer to the Django documentation for more information about
the fixtures.