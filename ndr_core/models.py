"""
models.py contains ndr_core's database models.
"""
import os.path

from ckeditor_uploader.fields import RichTextUploadingField
from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse, NoReverseMatch

from ndr_core.ndr_settings import NdrSettings


class NdrCoreSearchField(models.Model):
    """A NdrCoreSearch field servers two purposes: First it can produce a HTML form field and second its information
      is used to formulate an API request."""

    class FieldType(models.IntegerChoices):
        """The FieldType of a searchField is used to render the HTML form """

        STRING = 1, "String"
        """This type produces a text field"""

        NUMBER = 2, "Number"
        """This type produces a number field"""

        LIST = 3, "Dropdown List"
        """This field produces a dropdown or multi select field"""

        MULTI_LIST = 4, "Multi Select List"
        """This field produces a multi select field"""

        BOOLEAN = 5, "Boolean"
        """This type produces a checkbox"""

        DATE = 6, "Date"
        """This type produces a date field"""

        DATE_RANGE = 7, "Date Range"
        """This type produces a date range field"""

        NUMBER_RANGE = 8, "Number Range"
        """This type produces a number range field"""

        HIDDEN = 9, "Hidden"
        """This type produces a hidden field"""

        INFO_TEXT = 10, "Info Text"
        """This type produces a HTML component to show info text. This is not an input field"""

    field_name = models.CharField(max_length=100,
                                  primary_key=True,
                                  help_text="Choose a name for the field. Can't contain spaces or special characters"
                                            "and must be unique")
    """The field_name is used as the HTML form name"""

    field_label = models.CharField(max_length=100,
                                   help_text="This is the form field's label")
    """The field_label is the label for the HTML form field"""

    field_type = models.PositiveSmallIntegerField(choices=FieldType.choices,
                                                  default=FieldType.STRING,
                                                  help_text="Type of the form field. String produces a text field, "
                                                            "Number a number field and dictionary a dropdown.")
    """Type of the form field. This translates to the HTML input type"""

    field_required = models.BooleanField(default=False,
                                         help_text="Does this field need to be filled out?")
    """Sets a field to 'required' which means it can't be blank"""

    help_text = models.CharField(max_length=250,
                                 blank=True,
                                 default='',
                                 help_text="The help text which will be displayed in the form")
    """The help text which will be displayed in the form"""

    api_parameter = models.CharField(max_length=100,
                                     blank=True,
                                     default='',
                                     help_text="The name of the API parameter which is used to generate a query")
    """The name of the API parameter which is used to generate a query"""

    schema_name = models.CharField(max_length=100,
                                   null=True,
                                   help_text="Name of the schema this search_field is created from")
    """If the search fields were created from a schema, this field gets filled out with the schema's name. This helps
    to identify fields which were automatically created so they can be overwritten when they are regenerated from a 
    schema"""

    list_choices = models.TextField(blank=True,
                                    default='',
                                    help_text="Comma separated list of choices for dropdowns")
    """Comma separated list of choices for dropdowns"""

    lower_value = models.IntegerField(null=True,
                                      blank=True,
                                      help_text="The lower value of a range field")
    """The lower value of a range field"""

    upper_value = models.IntegerField(null=True,
                                      blank=True,
                                      help_text="The upper value of a range field")
    """The upper value of a range field"""

    use_in_csv_export = models.BooleanField(default=False,
                                            help_text="Should this field be included in the CSV export?")

    def get_list_choices(self):
        # read the list choices from the list_choices field
        # TODO ignore invalid lines
        list_choices = []
        if self.field_type == self.FieldType.LIST or self.field_type == self.FieldType.MULTI_LIST:
            list_choices = [tuple(line.split(',')[0:2]) for line in self.list_choices.splitlines()]
        return list_choices

    def get_list_choices_as_dict(self):
        # read the list choices from the list_choices field
        # TODO ignore invalid lines
        list_choices = {}
        if self.field_type == self.FieldType.LIST or self.field_type == self.FieldType.MULTI_LIST:
            list_choices = {line.split(',')[0]: line.split(',')[1] for line in self.list_choices.splitlines()}
        return list_choices

    def __str__(self):
        return f'{self.field_name} ({self.field_label})'


class NdrCoreSearchFieldFormConfiguration(models.Model):
    """Search fields can be used in forms. In order to place them, they can be configured to fit in a grid with
     a NdrCoreSearchFieldFormConfiguration."""

    search_field = models.ForeignKey(NdrCoreSearchField,
                                     on_delete=models.CASCADE,
                                     help_text="The search field to place in a form")
    """The search field to place in a form"""

    field_row = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)],
                                    help_text="The row in the form. Starts with 1.")
    """The row in the form. Starts with 1. """

    field_column = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)],
                                       help_text="The column in the form. Is a value between 1 and 12.")
    """The column in the form. Is a value between 1 and 12"""

    field_size = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)],
                                     help_text="The size of the field. Is a value between 1 and 12.")
    """The size of the field. Is a value between 1 and 12"""

    def __str__(self):
        return f'{self.search_field.field_label} (R{self.field_row}/C{self.field_column}/S{self.field_size})'


class NdrCoreApiImplementation(models.Model):
    """NDR Core has different API implementations to target different APIS. They are saved in this model. """

    name = models.CharField(max_length=100, primary_key=True)
    """Name of the API implementation. Used as identifier, can't contain special characters. """

    label = models.CharField(max_length=100, unique=True)
    """Display Label of the implementation. """

    url = models.URLField(null=True, blank='True')
    """URL of API homepage or documentation. """

    description = models.TextField(default='blank')
    """Description of this implementation. """

    supports_simple = models.BooleanField(default=True)
    """True if the API supports a catch all search with a simple search term. """

    supports_simple_and_or = models.BooleanField(default=True)
    """True if the API supports an AND and OR option for the simple search. """

    supports_advanced = models.BooleanField(default=True)
    """True if the API supports a field based search where different search values can be searched for different 
    fields."""

    supports_lists = models.BooleanField(default=True)
    """True if the API supports static lists which can be requested by an API query. """

    supports_facets = models.BooleanField(default=False)
    """True if the different values of a result are grouped in filter options. """

    supports_single_result = models.BooleanField(default=False)
    """True if a single result can be downloaded. """

    def __str__(self):
        return self.label


class NdrCoreApiConfiguration(models.Model):
    """An API configuration contains all necessary information to create a query to an API endpoint. """

    class Protocol(models.IntegerChoices):
        """Defines the protocol of the API configuration """
        HTTP = 1, "http"
        HTTPS = 2, "https"

    api_name = models.CharField(max_length=100,
                                verbose_name="API Name",
                                primary_key=True,
                                help_text="The (form) name of the API. Can't contain special characters or spaces.")
    """This name is used as identifier for the API Can't contain special characters or spaces"""

    api_host = models.CharField(max_length=100,
                                verbose_name="API Host",
                                help_text="The API host (domain only, e.g. my-api-host.org)")
    """The API host (domain only, e.g. my-api-host.org) """

    api_protocol = models.PositiveSmallIntegerField(choices=Protocol.choices,
                                                    verbose_name="Protocol",
                                                    default=Protocol.HTTPS,
                                                    help_text="The protocol used (http or https)")
    """The protocol used (http or https) """

    api_type = models.ForeignKey(NdrCoreApiImplementation, on_delete=models.CASCADE,
                                 verbose_name="API Type",
                                 help_text="Choose the API implementation of your configuration.")
    """Refers to the API implementation used for this configuration."""

    api_port = models.IntegerField(default=80,
                                   verbose_name="Port",
                                   help_text="Port to connect to.")
    """The TCP port of the API """

    api_label = models.CharField(max_length=250,
                                 verbose_name="Displayable Label",
                                 help_text="The API's label is the title of the queried repository. "
                                           "Choose a short descriptive title.")
    """The API's label is the title of the queried repository """

    api_description = models.TextField(default='',
                                       verbose_name="Description",
                                       help_text="Description of this configuration")
    """Description of this configuration."""

    api_page_size = models.IntegerField(default=10,
                                        verbose_name="Page Size",
                                        help_text="Size of the result page (e.g. 'How many results at once')")
    """The query results will return a page of the results. You can define the page size"""

    api_url_stub = models.CharField(default=None, null=True, blank=True, max_length=50,
                                    verbose_name="URL stub",
                                    help_text="Static URL part after host, before API parameters.")
    """Static URL part after host, before API parameters."""

    api_repository_url = models.URLField(default=None, null=True, blank=True,
                                         verbose_name="Repository URL",
                                         help_text="URL to the data repository where this data is stored.")
    """URL to the repository's website."""

    api_user_name = models.CharField(max_length=50, blank=True, default='',
                                     help_text="If the API needs user authentication, you can provide your username")
    """An API might need to authenticate a user with username/password credentials. """

    api_password = models.CharField(max_length=50, blank=True, default='',
                                    help_text="If the API needs user authentication, you can provide the password")
    """An API might need to authenticate a user with username/password credentials. """

    api_auth_key = models.CharField(max_length=512, blank=True, default='',
                                    help_text="If the API needs user authentication, you can provide an authentication "
                                              "key")
    """An API might need an authentication key to function. """

    def get_base_url(self):
        """
        Get the base URL for a configured API
        :return: base URL for a configured API
        """
        api_base_url = f'{self.get_api_protocol_display()}://{self.api_host}:{self.api_port}/'
        if self.api_url_stub is not None:
            api_base_url += self.api_url_stub + "/"
        return api_base_url

    def get_number_of_test_files(self):
        path = f"{NdrSettings.get_sample_data_path()}/{self.api_name}"
        if os.path.exists(path):
            return len(os.listdir(path))
        return 0

    def get_test_files(self):
        path = f"{NdrSettings.get_sample_data_path()}/{self.api_name}"
        if os.path.exists(path):
            return os.listdir(path)
        return []

    def __str__(self):
        return f'{self.api_name} ({self.api_label})'


class NdrCoreSearchConfiguration(models.Model):
    """ A search configuration describes a configured search form which targets a specified API configuration. """

    conf_name = models.CharField(max_length=100,
                                 primary_key=True,
                                 help_text="Name of this search configuration. "
                                           "Can't contain spaces or special characters.")
    """Name of the search configuration. Can't contain spaces or special characters. Can't be 'simple' """

    conf_label = models.CharField(max_length=100,
                                  unique=True,
                                  help_text="Label of this search configuration")
    """Name of the search configuration """

    api_configuration = models.ForeignKey(NdrCoreApiConfiguration,
                                          on_delete=models.CASCADE,
                                          help_text="The API to query")
    """The API to send the query to """

    search_form_fields = models.ManyToManyField(NdrCoreSearchFieldFormConfiguration,
                                                help_text="Fields associated with this configuration")
    """Fields associated with this configuration """

    search_has_compact_result = models.BooleanField(default=False,
                                                    help_text="If the result has a normal and a compact view, "
                                                              "check this box.")
    """If the result has a normal and a compact view, check this box."""

    def __str__(self):
        return self.conf_name

    @staticmethod
    def get_simple_search_mockup_config(api_configuration):
        """All search related functions expect a SearchConfiguration but the simple search only provides an
                ApiConfiguration. This returns a mockup config with the simple-search-api-configuration."""

        search_config = NdrCoreSearchConfiguration()
        search_config.api_configuration = api_configuration
        search_config.conf_name = 'simple'
        search_config.search_has_compact_result = NdrCoreValue.get_or_initialize('search_simple_has_compact_result_view',
                                                                                 init_value="false",
                                                                                 init_type=NdrCoreValue.ValueType.BOOLEAN).get_value()
        return search_config


class NdrCoreResultMapping(models.Model):
    """An NDR Core Result template mapping maps result jsons to html templates."""



class NdrCoreResultTemplateField(models.Model):
    """An NdrCoreResultTemplateField maps a json-result-value to a template-value """

    class Renderer(models.IntegerChoices):
        URL = 1, "url-link"
        GEONAMES = 2, "geonames.org"

    class Container(models.TextChoices):
        OPTIONS = "options", "Options"
        VALUE_LIST = "values", "Value List"

    belongs_to = models.ForeignKey(NdrCoreResultMapping, on_delete=models.CASCADE)
    """TODO """

    target_field_name = models.CharField(max_length=100)
    """Field name of the resulting structured response which is used to render a result line"""

    source_field_name = models.CharField(max_length=100)
    """Field name of the raw search result json. Nested objects are separated by '.'"""

    alternate_field_name = models.CharField(max_length=100, null=True, blank=True)
    """Field name of the raw search result json.  Used if 'source_field_name' does not exist or its value is None."""

    field_none_value = models.CharField(max_length=100, default='')
    """Displayed value if both 'source_field_name' and 'alternate_field_name' are None. """

    field_label = models.CharField(max_length=100, null=True, blank=True)
    """TODO """

    field_container = models.CharField(max_length=100, choices=Container.choices)
    """TODO """

    field_renderer = models.IntegerField(choices=Renderer.choices, null=True, blank=True)
    """TODO """


class NdrCoreFilterableListConfiguration(models.Model):
    """TODO """

    list_name = models.CharField(max_length=100, unique=True)
    """TODO """

    api_configuration = models.ForeignKey(NdrCoreApiConfiguration, on_delete=models.CASCADE, help_text="TODO")
    """TODO """


class NdrCorePage(models.Model):
    """ An NdrCorePage is a web page on the ndr_core website instance. Each page has a type (see PageType) and upon
     creation, a HTML template is created and saved in the projects template folder. This allows users to create
     pages over the administration interface and then adapt its contents as needed."""

    class PageType(models.IntegerChoices):
        """Ndr Core can display multiple page types which are listed in this choice class """

        TEMPLATE = 1, "Template Page"
        """A template page is a static page. A HTML template is created which can be filled with any content"""

        SIMPLE_SEARCH = 2, "Simple Search"
        """A simple search page is a page which contains a form with a single catch-all search field"""

        SEARCH = 3, "Custom Search"
        """A search page features a configured search form which contains a number of search fields"""

        COMBINED_SEARCH = 4, "Simple/Custom Search"
        """A combined search page contains both a simple and a configured search form which search the same repo."""

        CONTACT = 5, "Contact Form"
        """A contact from page displays a form to send a message to the project team"""

        FILTER_LIST = 6, "Filterable List"
        """A filter list page shows a list of data which can be filtered down"""

        FLIP_BOOK = 7, "Flip Book"
        """TODO """

        ABOUT_PAGE = 8, "About Us Page"
        """TODO """

    view_name = models.CharField(max_length=200,
                                 help_text='The url part of your page (e.g. https://yourdomain.org/p/view_name)',
                                 unique=True)
    """The view_name is part of the page url in the form: https://yourdomain.org/p/view_name"""

    page_type = models.IntegerField(choices=PageType.choices,
                                    default=PageType.TEMPLATE,
                                    help_text="Choose a type for your page.")
    """The page_type determines what kind of page is generated and what View is called (see PageType)"""

    name = models.CharField(verbose_name="Page Title",
                            max_length=200,
                            help_text="The name of the page, e.g. the page's title")
    """This is the name/title of the page. It will be displayed as a <h2>title</h2>"""

    label = models.CharField(max_length=200,
                             help_text="The label of the page, e.g. the page's navigation label")
    """This is the navigation label which is displayed in the navigation"""

    nav_icon = models.CharField(max_length=200,
                                help_text='The fontawesome nav icon (leave blank if none)',
                                blank=True)
    """For the navigation, fontawesome icons can be displayed (e.g. 'fas fa-home')"""

    index = models.IntegerField(default=0,
                                help_text='Page order')
    """The index determines the order the pages are displayed. 0 comes first (=most left)"""

    search_configs = models.ManyToManyField(NdrCoreSearchConfiguration)
    """If the page is of one of the search types (SEARCH, COMBINED_SEARCH), a number of search configurations can 
    be saved. """

    list_configs = models.ManyToManyField(NdrCoreFilterableListConfiguration)
    """If the page is of the List type, a list configuration can be saved. """

    simple_api = models.ForeignKey(NdrCoreApiConfiguration,
                                   null=True, blank=True,
                                   help_text='Api for simple search',
                                   on_delete=models.SET_NULL)
    """If the page is of type SIMPLE_SEARCH, a simple search configuration can be saved."""

    template_text = RichTextUploadingField(null=True, blank=True,
                                           help_text='Text for your template page')
    """Template Pages can be filled with RichText content (instead of 'manual' HTML). """

    parent_page = models.ForeignKey('NdrCorePage', null=True, blank=True, default=None, on_delete=models.DO_NOTHING,
                                    help_text="If you want this page to be a sub-page of another one, you can"
                                              "choose the parent page here")
    """Any NDR Core page might have children. Currently used for flip book. In the future to be used as navigation 
    hierarchy."""

    def url(self):
        """Returns the url of a given page or '#' if none is found"""
        if not os.path.isdir(NdrSettings.APP_NAME):
            return '#'

        try:
            reverse_url = reverse(f'{NdrSettings.APP_NAME}:{self.view_name}')
        except NoReverseMatch:
            try:
                reverse_url = reverse(f'{NdrSettings.APP_NAME}:ndr_view', kwargs={'ndr_page': self.view_name})
            except NoReverseMatch:
                reverse_url = '#'

        return reverse_url

    def __str__(self):
        return f"{self.name}: {self.label}"


class NdrCoreUiStyle(models.Model):
    """A NDR Core page is styled a certain way. Navigation may be on top or to the left, fonts may be different and
    so on. Each UI Style provides a base.html and (most probably) a css file."""

    name = models.CharField(max_length=100, primary_key=True)
    """Name of the style. Used as identifier. """

    label = models.CharField(max_length=100)
    """Human readable and descriptive label of the UI style."""

    filename = models.CharField(max_length=50)
    """Filename to save the base file and css with (no extension and no path information). """

    description = models.TextField()
    """Description of the style, highlighting its properties."""


class NdrCoreColorScheme(models.Model):
    """The NDR Core UI styles get colored with a certain color scheme. The selected scheme is used to create a
    colors.css stylesheet file in your ndr installation. It gets regenerated when you change the selected scheme."""

    scheme_name = models.CharField(primary_key=True,
                                   max_length=50,
                                   help_text='This name is used for export reference and as css file name. '
                                             'No spaces and no special characters but underscores.')
    """The name of the color scheme. For display and reference."""

    scheme_label = models.CharField(max_length=100,
                                    help_text='Human readable label of the scheme. Make it descriptive.')
    """Human readable label of the scheme """

    background_color = ColorField(help_text='Basic background color of the whole page.')
    """Basic background color of the whole page."""

    container_bg_color = ColorField(help_text='Basic container (cards, tables, etc.) color of the whole page.')
    """Basic container (cards, tables, etc.) color of the whole page."""

    text_color = ColorField(help_text='Basic text color for the whole page.')
    """Basic text color for the whole page."""

    title_color = ColorField(help_text='Title text color for the whole page.')
    """Title text color for the whole page."""

    button_color = ColorField(help_text='Background color of primary buttons.')
    """Background color of primary buttons."""

    button_hover_color = ColorField(help_text='Hover color of primary buttons.')
    """Hover color of primary buttons."""

    button_text_color = ColorField(help_text='Text color of primary buttons.')
    """Text color of primary buttons."""

    button_border_color = ColorField(help_text='Border color of primary buttons.')
    """Border color of primary buttons."""

    second_button_color = ColorField(help_text='Background color of secondary buttons.')
    """Basic color of secondary buttons."""

    second_button_hover_color = ColorField(help_text='Hover color of secondary buttons.')
    """Hover color of secondary buttons."""

    second_button_text_color = ColorField(help_text='Text color of secondary buttons.')
    """Text color of secondary buttons."""

    second_button_border_color = ColorField(help_text='Border color of secondary buttons.')
    """Border color of secondary buttons."""

    link_color = ColorField(help_text='Color for links.')
    """Color for hrefs."""

    form_field_bg = ColorField()
    form_field_fg = ColorField()

    footer_bg = ColorField()

    accent_color_1 = ColorField(help_text='Accent color 1. Used as navigation background and the like.')
    """Accent color 1."""

    accent_color_2 = ColorField(help_text='Accent color 2. Used as element background and the like.')
    """Accent color 2."""

    info_color = ColorField(help_text='Info color for alerts.')
    """Info color for alerts."""

    success_color = ColorField(help_text='Success color for alerts.')
    """Success color for alerts."""

    error_color = ColorField(help_text='Error color for alerts.')
    """Error color for alerts."""

    @staticmethod
    def color_list():
        return ['background_color', 'container_bg_color', 'footer_bg', 'text_color', 'title_color',
                'button_color', 'button_text_color', 'button_hover_color', 'button_border_color',
                'second_button_color', 'second_button_text_color', 'second_button_hover_color',
                'second_button_border_color',
                'form_field_bg', 'form_field_fg',
                'link_color', 'accent_color_1', 'accent_color_2', 'info_color', 'success_color', 'error_color']

    def __str__(self):
        return self.scheme_label


class NdrCoreValue(models.Model):
    """NdrCore provides a number of ready-to-use components which need to be configured with setting values. This data
     model stores these setting values. Example: A contact form has a subject field which can be prefilled with a string
     of choice. This string can be provided by this data model (value_name='contact_form_default_subject').
     The list of values is given and gets loaded from a fixture when the management command 'init_ndr_core' is
     executed. Users can only manipulate the 'value_value' of each object."""

    class ValueType(models.TextChoices):
        STRING = "string", "String"
        INTEGER = "integer", "Integer"
        BOOLEAN = "boolean", "Boolean"
        LIST = "list", "List"
        URL = "url", "URL"

    value_name = models.CharField(max_length=100, primary_key=True,
                                  help_text='This is the identifier of a NdrCoreValue. '
                                            'Can\'t contain special characters.' )
    """This is the identifier of a NdrCoreValue. In the source, each value gets loaded by searching for this name"""

    value_type = models.CharField(choices=ValueType.choices,
                                  max_length=10,
                                  help_text="The type of your value",
                                  default=ValueType.STRING)

    value_label = models.CharField(max_length=100,
                                   help_text='This is a human readable label for the value. '
                                             'It is used in the admin view forms.')
    """This is a human readable label for the value (e.g. its title)"""

    value_help_text = models.CharField(max_length=250,
                                       help_text='This is the help text of the form field.')
    """This is the help text for a value which explains to users what it is for"""

    value_value = models.CharField(max_length=100,
                                   help_text='This is the actual value which can be updated')
    """This is the actual value which can be updated by the user"""

    value_options = models.CharField(max_length=200, default='',
                                     help_text='Used for value_type LIST: comma-separated list')

    is_user_value = models.BooleanField(default=False)
    """Indicates if a value was created by a user"""

    def set_value(self, value):
        if self.value_type == NdrCoreValue.ValueType.BOOLEAN:
            if value:
                self.value_value = 'true'
            else:
                self.value_value = 'false'

    def get_value(self):
        """Returns the valued which is always saved as string as the proper type. """
        if self.value_type == NdrCoreValue.ValueType.STRING or self.value_type == NdrCoreValue.ValueType.LIST or \
                self.value_type == NdrCoreValue.ValueType.URL:
            return self.value_value
        if self.value_type == NdrCoreValue.ValueType.INTEGER:
            try:
                return int(self.value_value)
            except (TypeError, ValueError):
                return 0
        if self.value_type == NdrCoreValue.ValueType.BOOLEAN:
            if self.value_value.lower() == 'true' or self.value_value.lower() == 'on' or self.value_value == 'on':
                return True
            else:
                return False

    def get_options(self):
        """For lists there are options, saved as string in the form: (key1,value1);(key2,value2)"""
        if self.value_type == NdrCoreValue.ValueType.LIST:
            options = list()
            option_tuples = self.value_options.split(";")
            for ot in option_tuples:
                options.append(ot.split(','))
            return options
        return None

    @staticmethod
    def get_or_initialize(value_name, init_value=None, init_label=None, init_type=ValueType.STRING):
        """Returns or creates an NdrCoreValue object. """
        try:
            return NdrCoreValue.objects.get(value_name=value_name)
        except NdrCoreValue.DoesNotExist:
            if init_value is None:
                init_value = ''
            if init_label is None:
                init_label = value_name
            return NdrCoreValue.objects.create(value_name=value_name,
                                               value_value=init_value,
                                               value_label=init_label,
                                               value_type=init_type)

    def __str__(self):
        return self.value_name


class NdrCoreDataSchema(models.Model):
    """NdrCore provides a number of already implemented schemas. For each schema it is known which search fields are
     possible so they can be generated automatically. Example: NdrCore has a 'Historic Person Instances' schema
     implemented for which we know we can search for last and given names, organization affiliation and locations
     (etc.). So we provide a django-fixture to automatically create these NdrCoreSearchField objects to use them in
     a search form.
     The list of available schemas is loaded when the management command 'init_ndr_core' is executed and can not
     be manipulated by users."""

    schema_url = models.URLField()
    """This is a stable URL of the implemented schema"""

    schema_label = models.CharField(max_length=100)
    """This is a human readable label for the schema (e.g. its title)"""

    schema_name = models.CharField(max_length=100)
    """This is the name of the schema (e.g. its identifier within ndrCore)"""

    fixture_name = models.CharField(max_length=100)
    """This is the filename of the fixture to load the search fields from. This contains only the file name which must
    be available in the ndr_core module in 'ndr_core/fixtures/'"""


class NdrCoreCorrection(models.Model):
    """Users can be given the opportunity to correct entries which have errors. Each correction can consist of
     multiple field corrections. Users need to provide an ORCID. This does not automatically correct data
     but administrators can accept or reject corrections."""

    corrected_dataset = models.ForeignKey(NdrCoreApiConfiguration,
                                          on_delete=models.CASCADE)
    """TODO """

    corrected_record_id = models.CharField(max_length=255)
    """TODO """

    corrector_orcid = models.CharField(max_length=50)
    """TODO """


class NdrCoreCorrectedField(models.Model):
    """TODO """

    ndr_correction = models.ForeignKey(NdrCoreCorrection,
                                       on_delete=models.CASCADE)
    """TODO """

    field_name = models.CharField(max_length=100)
    """TODO """

    old_value = models.TextField()
    """TODO """

    new_value = models.TextField()
    """TODO """


class NdrCoreUserMessage(models.Model):
    """If the contact form is sent, a user message object is created. """

    message_subject = models.CharField(max_length=200)
    """TODO """

    message_text = models.TextField()
    """TODO """

    message_time = models.DateTimeField(auto_now_add=True)
    """TODO """

    message_ret_email = models.EmailField()
    """TODO """

    message_archived = models.BooleanField(default=False)
    """Indicates if the message has been archived.  """

    message_forwarded = models.BooleanField(default=False)
    """Indicates if the messagge has been forwarded to a specified e-mail address. """

    def __str__(self):
        return f"{self.message_subject} (from: {self.message_ret_email})"


class NdrCoreSearchStatisticEntry(models.Model):
    """Every time a search is executed, a NdrCoreSearchStatisticEntry object is created if the setting
    'statistics_feature' is set to 'true' """

    search_api = models.ForeignKey(NdrCoreApiConfiguration, on_delete=models.CASCADE)
    """The API which was queried in the search. """

    search_term = models.CharField(max_length=100, default='')
    """The search term(s) which have been searched. """

    search_query = models.CharField(max_length=255, default='')
    """TODO"""

    search_no_results = models.IntegerField(default=0)
    """TODO"""

    search_time = models.DateTimeField(auto_now_add=True)
    """The time the user searched. """

    search_location = models.CharField(max_length=20, null=True)
    """The location the user searched from. """


class NdrCoreImage(models.Model):
    """ Directory of all images used outside the ckeditor and the logo. """

    class ImageGroup(models.TextChoices):
        BGS = "backgrounds", "Background Images"
        ELEMENTS = "elements", "Slideshow Images"
        FIGURES = "figures", "Figures"
        LOGOS = "logos", "Partner Images"
        PEOPLE = "people", "People"

        @staticmethod
        def get_label_by_value(group_value, choices):
            for choice in choices:
                if choice[0] == group_value:
                    return choice[1]

    title = models.CharField(max_length=200, blank=True, default='',
                             help_text='Title of the image.')
    """Title of the image"""

    caption = models.CharField(max_length=200, blank=True, default='',
                               help_text='Caption of the image.')
    """Caption of the image"""

    citation = models.CharField(max_length=200, blank=True, default='',
                                help_text='Citation text of the image.')
    """Source of the image"""

    url = models.URLField(null=True, blank=True, default=None,
                          help_text='URL to image or source')
    """URL to image or source"""

    image = models.ImageField(upload_to='images',
                              help_text='Upload an image file')
    """Actual image"""

    image_group = models.CharField(max_length=100,
                                   choices=ImageGroup.choices)
    """Group the image belongs to. """

    index_in_group = models.IntegerField(default=0)
    """For ordering the images within the group. """

    image_active = models.BooleanField(default=True)
    """To indicate that this image is not to be used in automatic collections."""

    def get_absolute_url(self):
        return reverse('ndr_core:view_images', kwargs={'group': self.image_group})

    def __str__(self):
        return self.title


class NdrCoreUpload(models.Model):
    title = models.CharField(max_length=200, blank=True, default='',
                             help_text='Title of the upload.')
    """Title of the upload"""

    file = models.FileField(upload_to='uploads/')
    """Actual file"""


class NdrCoreUIElement(models.Model):
    """ UI Element """

    class UIElementType(models.TextChoices):
        CARD = "card", "Card"
        SLIDESHOW = "slides", "Slideshow"
        CAROUSEL = "carousel", "Carousel"
        JUMBOTRON = "jumbotron", "Jumbotron"
        IFRAME = "iframe", "IFrame"
        BANNER = "banner", "Banner"

        def get_(self):
            pass

    type = models.CharField(max_length=100,
                            choices=UIElementType.choices)
    """Type of the element. Decides how it is rendered. """

    title = models.CharField(max_length=100,
                             help_text='Title of the element for your reference.')
    """TODO """

    use_image_conf = models.BooleanField(default=True,
                                         help_text='Use the image\'s title, caption and URL?')
    """TODO """

    show_indicators = models.BooleanField(default=True,
                                          help_text='Show the indicators for slideshows and carousels?')
    """TODO """

    show_title = models.BooleanField(default=True,
                                     help_text='Show the title?')
    """TODO """

    show_text = models.BooleanField(default=True,
                                    help_text='Show the element\'s text?')
    """TODO """

    show_image = models.BooleanField(default=True,
                                     help_text='Show the images?')
    """TODO """

    link_element = models.BooleanField(default=True,
                                       help_text='Link the elements to the supplied url?')
    """TODO """

    autoplay = models.BooleanField(default=False,
                                   help_text='Autoplay carousels and slideshows?')
    """TODO """

    def items(self):
        """TODO """
        return self.ndrcoreuielementitem_set.all().order_by('order_idx')

    def get_absolute_url(self):
        return reverse('ndr_core:view_ui_element', kwargs={'pk': self.pk})


class NdrCoreUiElementItem(models.Model):
    """TODO """

    belongs_to = models.ForeignKey(NdrCoreUIElement, on_delete=models.CASCADE)
    """TODO """

    order_idx = models.IntegerField()
    """TODO """

    ndr_image = models.ForeignKey(NdrCoreImage, on_delete=models.CASCADE, null=True)
    """TODO """

    title = models.CharField(max_length=100, blank=True)
    """TODO """

    text = models.TextField(blank=True)
    """TODO """

    url = models.URLField(blank=True)
    """TODO """
