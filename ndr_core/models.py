"""
models.py contains ndr_core's database models.
"""
from ckeditor_uploader.fields import RichTextUploadingField
from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse, NoReverseMatch

from ndr_core.ndr_settings import NdrSettings


class NdrSearchField(models.Model):
    """A NdrCoreSearch field servers two purposes: First it can produce a HTML form field and second its information
      is used to formulate an API request."""

    class FieldType(models.IntegerChoices):
        """The FieldType of a searchField is used to render the HTML form """

        STRING = 1, "String"
        """This type produces a text field"""

        NUMBER = 2, "Number"
        """This type produces a number field"""

        DICTIONARY = 3, "Dictionary"
        """This field produces a dropdown or multi select field"""

    field_name = models.CharField(max_length=100,
                                  unique=True,
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
                                 help_text="The help text which will be displayed in the form")
    """The help text which will be displayed in the form"""

    api_parameter = models.CharField(max_length=100,
                                     help_text="The name of the API parameter which is used to generate a query")
    """The name of the API parameter which is used to generate a query"""

    schema_name = models.CharField(max_length=100,
                                   null=True,
                                   help_text="Name of the schema this search_field is created from")
    """If the search fields were created from a schema, this field gets filled out with the schema's name. This helps
    to identify fields which were automatically created so they can be overwritten when they are regenerated from a 
    schema"""

    def __str__(self):
        return f'{self.field_name} ({self.field_label})'


class SearchFieldFormConfiguration(models.Model):
    """Search fields can be used in forms. In order to place them, they can be configured to fit in a grid with
     a SearchFieldFormConfiguration."""

    search_field = models.ForeignKey(NdrSearchField,
                                     on_delete=models.CASCADE,
                                     help_text="The search field to place in a form")
    """The search field to place in a form"""

    field_row = models.IntegerField(help_text="The row in the form. Starts with 1.")
    """The row in the form. Starts with 1. """

    field_column = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)],
                                       help_text="The column in the form. Is a value between 1 and 12.")
    """The column in the form. Is a value between 1 and 12"""

    field_size = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)],
                                     help_text="The size of the field. Is a value between 1 and 12.")
    """The size of the field. Is a value between 1 and 12"""

    def __str__(self):
        return f'{self.search_field.field_label} (R{self.field_row}/C{self.field_column}/S{self.field_size})'


class ApiConfiguration(models.Model):
    """An API configuration contains all necessary information to create a query to an API endpoint. """

    class Protocol(models.IntegerChoices):
        """Defines the protocol of the API configuration """
        HTTP = 1, "http"
        HTTPS = 2, "https"

    api_name = models.CharField(max_length=100,
                                unique=True,
                                help_text="The (form) name of the API. Can't contain special characters or spaces")
    """This name is used as identifier for the API Can't contain special characters or spaces"""

    api_host = models.CharField(max_length=100,
                                help_text="The API host (domain only, e.g. my-api-host.org)")
    """The API host (domain only, e.g. my-api-host.org) """

    api_protocol = models.PositiveSmallIntegerField(choices=Protocol.choices,
                                                    default=Protocol.HTTPS,
                                                    help_text="The protocol used (http or https)")
    """The protocol used (http or https) """

    api_port = models.IntegerField(default=80,
                                   help_text="TODO")
    """The TCP port of the API """

    api_label = models.CharField(max_length=250,
                                 help_text="The API's label is the title of the queried repository")
    """The API's label is the title of the queried repository """

    api_page_size = models.IntegerField(default=10,
                                        help_text="Size of the result page (e.g. 'How many results at once')")
    """The query results will return a page of the results. You can define the page size"""

    def get_base_url(self):
        """
        Get the base URL for a configured API
        :return: base URL for a configured API
        """
        return f'{self.get_api_protocol_display()}://{self.api_host}:{self.api_port}/'

    def __str__(self):
        return f'{self.api_name} ({self.api_label})'


class SearchConfiguration(models.Model):
    """ A search configuration contains TODO """

    conf_name = models.CharField(max_length=100,
                                 unique=True,
                                 help_text="Name of this search configuration. "
                                           "Can't contain spaces or special characters.")
    """Name of the search configuration. Can't contain spaces or special characters. Can't be 'simple' """

    conf_label = models.CharField(max_length=100,
                                  unique=True,
                                  help_text="Label of this search configuration")
    """Name of the search configuration """

    api_configuration = models.ForeignKey(ApiConfiguration,
                                          on_delete=models.CASCADE,
                                          help_text="The API to query")
    """The API to query """

    search_form_fields = models.ManyToManyField(SearchFieldFormConfiguration,
                                                help_text="Fields associated with this configuration")
    """Fields associated with this configuration """

    def __str__(self):
        return self.conf_name


class FilterableListConfiguration(models.Model):
    """TODO """

    list_name = models.CharField(max_length=100, unique=True)
    """TODO """

    api_configuration = models.ForeignKey(ApiConfiguration, on_delete=models.CASCADE, help_text="TODO")
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

    view_name = models.CharField(max_length=200,
                                 help_text='The url part of your page (e.g. https://yourdomain.org/p/view_name)',
                                 unique=True)
    """The view_name is part of the page url in the form: https://yourdomain.org/p/view_name"""

    page_type = models.IntegerField(choices=PageType.choices,
                                    default=PageType.TEMPLATE,
                                    help_text="Choose a type for your page. Template is a static page, search pages"
                                              "display search forms, a filtered list displays data resources with a"
                                              "filter, contact form displays a form to send a message.")
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

    search_configs = models.ManyToManyField(SearchConfiguration)
    """If the page is of one of the search types (SEARCH, COMBINED_SEARCH), a number of search configurations can 
    be saved. """

    list_configs = models.ManyToManyField(FilterableListConfiguration)
    """If the page is of the List type, a list configuration can be saved. """

    simple_api = models.ForeignKey(ApiConfiguration,
                                   null=True, blank=True,
                                   help_text='Api for simple search',
                                   on_delete=models.SET_NULL)
    """If the page is of type SIMPLE_SEARCH, a simple search configuration can be saved."""

    template_text = RichTextUploadingField(null=True, blank=True,
                                           help_text='Text for your template page')
    """Template Pages can be filled with RichText content (instead of 'manual' HTML). """

    def url(self):
        """Returns the url of a given page or '#' if none is found"""
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

    name = models.CharField(max_length=100, unique=True)
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

    scheme_name = models.CharField(unique=True, max_length=50)
    """The name of the color scheme. For display and reference."""

    scheme_label = models.CharField(max_length=100)
    """Human readable label of the scheme """

    background_color = ColorField()
    """Basic background color of the whole page."""

    text_color = ColorField()
    """Basic text color for the whole page."""

    button_color = ColorField()
    """Basic color of primary buttons."""

    button_hover_color = ColorField()
    """Hover color of primary buttons."""

    button_text_color = ColorField()
    """Text color of primary buttons."""

    button_border_color = ColorField()
    """Border color of primary buttons."""

    second_button_color = ColorField()
    """Basic color of secondary buttons."""

    second_button_hover_color = ColorField()
    """Hover cover of secondary buttons."""

    second_button_text_color = ColorField()
    """Text color of secondary buttons."""

    second_button_border_color = ColorField()
    """Border colorof secondary buttons."""

    link_color = ColorField()
    """Color for hrefs."""

    accent_color_1 = ColorField()
    """Accent color 1."""

    accent_color_2 = ColorField()
    """Accent color 2."""

    info_color = ColorField()
    """Info color for alerts."""

    success_color = ColorField()
    """Success color for alerts."""

    error_color = ColorField()
    """Error color for alerts."""


class NdrCoreValue(models.Model):
    """NdrCore provides a number of ready-to-use components which need to be configured with setting values. This data
     model stores these setting values. Example: A contact form has a subject field which can be prefilled with a string
     of choice. This string can be provided by this data model (value_name='contact_form_default_subject').
     The list of values is given and gets loaded from a fixture when the management command 'init_ndr_core' is
     executed. Users can only manipulate the 'value_value' of each object."""

    value_name = models.CharField(max_length=100, unique=True)
    """This is the identifier of a NdrCoreValue. In the source, each value gets loaded by searching for this name"""

    value_label = models.CharField(max_length=100)
    """This is a human readable label for the value (e.g. its title)"""

    value_help_text = models.CharField(max_length=250)
    """This is the help text for a value which explains to users what it is for"""

    value_value = models.CharField(max_length=100)
    """This is the actual value which can be updated by the user"""

    @staticmethod
    def get_or_initialize(value_name, init_value=None, init_label=None):
        try:
            return NdrCoreValue.objects.get(value_name=value_name)
        except NdrCoreValue.DoesNotExist:
            if init_value is None:
                init_value = ''
            if init_label is None:
                init_label = value_name
            return NdrCoreValue.objects.create(value_name=value_name, value_value=init_value, value_label=init_label)


class NdrCoreDataSchema(models.Model):
    """NdrCore provides a number of already implemented schemas. For each schema it is known which search fields are
     possible so they can be generated automatically. Example: NdrCore has a 'Historic Person Instances' schema
     implemented for which we know we can search for last and given names, organization affiliation and locations
     (etc.). So we provide a django-fixture to automatically create these NdrSearchField objects to use them in
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


class NdrCorrection(models.Model):
    """Users can be given the opportunity to correct entries which have errors. Each correction can consist of
     multiple field corrections. Users need to provide an ORCID. This does not automatically correct data
     but administrators can accept or reject corrections."""

    corrected_dataset = models.ForeignKey(ApiConfiguration,
                                          on_delete=models.CASCADE)
    """TODO """

    corrected_record_id = models.CharField(max_length=255)
    """TODO """

    corrector_orcid = models.CharField(max_length=50)
    """TODO """


class NdrCorrectedField(models.Model):
    """TODO """

    ndr_correction = models.ForeignKey(NdrCorrection,
                                       on_delete=models.CASCADE)
    """TODO """

    field_name = models.CharField(max_length=100)
    """TODO """

    old_value = models.TextField()
    """TODO """

    new_value = models.TextField()
    """TODO """
