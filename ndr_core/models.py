from django.db import models
from django.urls import reverse, NoReverseMatch

from ndr_core.ndr_settings import NdrSettings


class NdrCorePage(models.Model):
    """ An NdrCorePage is a page on the ndr_core website instance. """

    class PageType(models.IntegerChoices):
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
    class FieldType(models.IntegerChoices):
        STRING = 1, "String"
        NUMBER = 2, "Number"
        DICTIONARY = 3, "Dictionary"

    field_name = models.CharField(max_length=100)
    field_label = models.CharField(max_length=100)
    field_type = models.PositiveSmallIntegerField(choices=FieldType.choices, default=FieldType.STRING)
    field_required = models.BooleanField(default=False)
    help_text = models.CharField(max_length=250)
    api_parameter = models.CharField(max_length=100)
    schema_name = models.CharField(max_length=100, null=True)


class ApiConfiguration(models.Model):
    class Protocol(models.IntegerChoices):
        HTTP = 1, "http"
        HTTPS = 2, "https"

    api_name = models.CharField(max_length=100, unique=True)
    api_host = models.CharField(max_length=100)
    api_protocol = models.PositiveSmallIntegerField(choices=Protocol.choices, default=Protocol.HTTPS)
    api_port = models.IntegerField(default=80)
    api_label = models.CharField(max_length=250)
    api_page_size = models.IntegerField(default=10)


class SearchFieldFormConfiguration(models.Model):
    search_field = models.ForeignKey(NdrSearchField, on_delete=models.CASCADE)
    field_row = models.IntegerField()
    field_column = models.IntegerField()
    field_size = models.IntegerField()


class SearchConfiguration(models.Model):
    """ A search configuration contains """

    api_configuration = models.ForeignKey(ApiConfiguration, on_delete=models.CASCADE)
    search_form_fields = models.ManyToManyField(SearchFieldFormConfiguration)


class NdrCoreValue(models.Model):
    value_name = models.CharField(max_length=100, unique=True)
    value_label = models.CharField(max_length=100)
    value_help_text = models.CharField(max_length=250)
    value_value = models.CharField(max_length=100)


class NdrCoreDataSchema(models.Model):
    schema_url = models.URLField()
    schema_label = models.CharField(max_length=100)
    schema_name = models.CharField(max_length=100)
    fixture_name = models.CharField(max_length=100)
