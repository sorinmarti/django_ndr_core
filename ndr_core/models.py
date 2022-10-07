"""
models.py contains ndr_core's database models.
"""
from django.db import models
from django.urls import reverse, NoReverseMatch

from ndr_core.ndr_settings import NdrSettings


class NdrCorePage(models.Model):
    """ An NdrCorePage is a page on the ndr_core website instance. TODO """

    class PageType(models.IntegerChoices):
        """TODO """
        TEMPLATE = 1, "Template Page"
        SIMPLE_SEARCH = 2, "Simple Search"
        SEARCH = 3, "Custom Search"
        COMBINED_SEARCH = 4, "Simple/Custom Search"
        CONTACT = 5, "Contact Form"
        FILTER_LIST = 6, "Filterable List"

    view_name = models.CharField(max_length=200,
                                 help_text='The url part of your page (e.g. https://yourdomain.org/p/view_name)',
                                 unique=True)

    page_type = models.IntegerField(choices=PageType.choices, default=PageType.TEMPLATE)

    name = models.CharField(max_length=200,
                            help_text='The name of the page, e.g. the page\'s title')

    label = models.CharField(max_length=200,
                             help_text='The label of the page, e.g. the page\'s navigation label')

    nav_icon = models.CharField(max_length=200,
                                help_text='The fontawesome nav icon (leave blank if none)',
                                blank=True)

    index = models.IntegerField(default=0,
                                help_text='Page order')

    def url(self):
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


class NdrSearchField(models.Model):
    """TODO """

    class FieldType(models.IntegerChoices):
        """TODO """
        STRING = 1, "String"
        NUMBER = 2, "Number"
        DICTIONARY = 3, "Dictionary"

    field_name = models.CharField(max_length=100, help_text="TODO")
    field_label = models.CharField(max_length=100, help_text="TODO")
    field_type = models.PositiveSmallIntegerField(choices=FieldType.choices, default=FieldType.STRING, help_text="TODO")
    field_required = models.BooleanField(default=False, help_text="TODO")
    help_text = models.CharField(max_length=250, help_text="TODO")
    api_parameter = models.CharField(max_length=100, help_text="TODO")
    schema_name = models.CharField(max_length=100, null=True, help_text="TODO")


class ApiConfiguration(models.Model):
    """TODO """

    class Protocol(models.IntegerChoices):
        """TODO """
        HTTP = 1, "http"
        HTTPS = 2, "https"

    api_name = models.CharField(max_length=100, unique=True, help_text="TODO")
    api_host = models.CharField(max_length=100, help_text="TODO")
    api_protocol = models.PositiveSmallIntegerField(choices=Protocol.choices, default=Protocol.HTTPS, help_text="TODO")
    api_port = models.IntegerField(default=80, help_text="TODO")
    api_label = models.CharField(max_length=250, help_text="TODO")
    api_page_size = models.IntegerField(default=10, help_text="TODO")


class SearchFieldFormConfiguration(models.Model):
    """TODO """

    search_field = models.ForeignKey(NdrSearchField, on_delete=models.CASCADE, help_text="TODO")
    field_row = models.IntegerField(help_text="TODO")
    field_column = models.IntegerField(help_text="TODO")
    field_size = models.IntegerField(help_text="TODO")


class SearchConfiguration(models.Model):
    """ A search configuration contains TODO """

    api_configuration = models.ForeignKey(ApiConfiguration, on_delete=models.CASCADE, help_text="TODO")
    search_form_fields = models.ManyToManyField(SearchFieldFormConfiguration, help_text="TODO")


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
