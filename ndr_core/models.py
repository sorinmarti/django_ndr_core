from django.db import models
from django.urls import reverse, NoReverseMatch


class NdrCorePage(models.Model):
    """ An NdrCorePage is a page on the ndr_core website instance. """

    name = models.CharField(max_length=200,
                            help_text='The name of the page, e.g. the page\'s title')

    label = models.CharField(max_length=200,
                             help_text='The label of the page, e.g. the page\'s navigation label')

    view_name = models.CharField(max_length=200,
                                 help_text='The name of the view to display')

    nav_icon = models.CharField(max_length=200,
                                help_text='The fontawesome nav icon (leave blank if none)',
                                blank=True)

    index = models.IntegerField(default=0,
                                help_text='Page order')

    def url(self):
        try:
            reverse_url = reverse(f'main:{self.view_name}')
        except NoReverseMatch:
            reverse_url = '#'

        return reverse_url

    def __str__(self):
        return f"{self.name}: {self.label}"


class SearchField(models.Model):
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
    search_field = models.ForeignKey(SearchField, on_delete=models.CASCADE)
    field_row = models.IntegerField()
    field_column = models.IntegerField()
    field_size = models.IntegerField()


class SearchConfiguration(models.Model):
    """ A search configuration contains """

    api_configuration = models.ForeignKey(ApiConfiguration, on_delete=models.CASCADE)
    search_form_fields = models.ManyToManyField(SearchFieldFormConfiguration)


class NdrCoreValue(models.Model):
    value_name = models.CharField(max_length=100)
    value_label = models.CharField(max_length=100)
    value_help_text = models.CharField(max_length=100)
    value_value = models.CharField(max_length=100)