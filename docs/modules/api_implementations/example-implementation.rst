Example Implementation
======================

To provide some detailed insight on how to implement an API, a sample implementation is shown here.
It is not a valuable data example as it is a questionable database of
historical figures but it is a good example to show how to implement an API. The API
is called **Historical Figures** and is available from https://api-ninjas.com/api/historicalfigures/.
API Ninjas provides a number of APIs for testing purposes and this is
one of them. The listing below shows an example result sent back by API Ninjas for the
request https://api.api-ninjas.com/v1/historicalfigures?name=Bernoulli . The
results have been shortened for the sake of brevity and because the full result is not
needed to understand the implementation example. The base class is then able to create
pagination links, result labels, download buttons and other elements based on search
meta data.

::

    [
      {
        "name": "Nicolaus I Bernoulli",
        "title": "Swiss mathematician and theorist",
        "info": {}
      },
      {
        "name": "Jacob Bernoulli",
        "title": "Swiss mathematician and theorist",
        "info": {
            "born": "6 January 1655 Basel Switzerland",
            "died": "16 August 1705 Basel , Switzerland"
        }
     },
     {
        "name": "Daniel Bernoulli",
        "title": "Dutch - Swiss mathematician and physicist",
        "info": {
            "born": "8 February 1700 Groningen Dutch Republic",
            "died": "27 March 1782 Basel Republic of the Swiss"
        }
     },
     [...]
   ]


As one can see, the request is a simple HTTP request with a query string. The only
parameter is the name of the historical figure. The result is a JSON array of objects in
text form. NDR Core does not need to know about the structure of the content of the
result because the result displays can be configured to display any field of the result.
So the task for the ``ApiNinjasQuery`` class is to create a query string composed of the
base connection string (which is part of the search configuration) and supported query
parameters. Because this example only has name as a query parameter, the implementation
of the ``get_simple_query`` method is very simple.

This example is easy to implement because the result is already in a JSON format
and can be used by NDR Core without any conversions. The first step is to implement
the query methods as shown in Listing 4.9. It basically just consists of adding the name
parameter to the base string.

::

    def get_simple_query (self , search_term , and_or =’and ’):
        return self . get_base_string () + "? name =" + search_term

    def get_advanced_query (self , * kwargs ):
        query = self . get_base_string () + "?"

        for field_value in self . values :
            query += f"{ field_value }={ self . values [ field_value ]}"
        return query



Implementing the result class is also pretty straightforward. The result needs to be
saved into the memory to be used as display data in the front end. The data needs to be a
list of dictionaries, each dictionary represents one result. ``ApiNinjas`` already returns data
in this form but it needs to be converted from utf8 text to Python dictionaries. Python
has a library to do this, so this is only two lines of code in ``save_raw_result``. ApiNinjas
does not paginate, it always returns all results up to a maximum. This makes filling in
the result meta data easy: The total number of results is the size of the result list, the
page number is always 1, the page size always the size of the result and the number of
pages is always 1.

::

    def __init__(self, search_configuration, query, request ):
        super().__init__ ( search_configuration, query, request )
        self.api_request_headers['X-Api -Key'] = self.search_configuration.api_auth_key

    def save_raw_result (self , text ):
        """ API Ninjas returns a JSON response . Save it as dict , so it can
            be accessed easily. """

        try :
            json_obj = json.loads( text )
            self.raw_result = json_obj
            return
         except json.JSONDecodeError:
            self.error = _(" Result could not be loaded ")
            self.error_code = BaseResult.LOADED
            return

    def fill_search_result_meta_data ( self ):
        """ Set the metadata for the search result ."""
        self.total = len( self.raw_result )
        self.page = 1
        self.page_size = self.total
        self.num_pages = 1



This already constitutes for a complete API implementation. There are two more details
which tie together the whole example with the configuration in the administration
interface and the multi-lingual nature of NDR Core. First, the default constructor adds
an X-Api-Key to the header of the HTTP request. This is ApiNinjas way of authenticating
users to their services. The search configuration form has fields
to enter authentication information which can be used in the API implementation. This
means that someone implementing an API can also implement authentication features
and such. Secondly, this example has an implementation of an error code. If the JSON
data cannot be decoded, an error code and an error message is set. The error code can
be defined or taken from the base class. It is used to log failed searches. The error
message must be coded in English as this is the software’s language. The underscore before
the string marks that this message is to be translated. When releasing a new version,
NDR Core will gather all messages that are marked to be translated and collect them in
PO files for the Gettext translation process (see Section 4.2.5). The message is displayed
to a database user if the error occurs. If it is translated, it will appear in the requested
language, if not it will appear in English.