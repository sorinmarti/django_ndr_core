"""models.py contains ndr_core's database models."""
import csv
import json
import os.path
from io import StringIO

from ckeditor_uploader.fields import RichTextUploadingField
from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils.translation import get_language, get_language_info
from django.utils.translation import gettext_lazy as _

from ndr_core.ndr_settings import NdrSettings

TRANSLATABLE_TABLES = (
    ('ndrcoresearchfield', 'Search Field Table'),
    ('ndrcoreresultfield', 'Result Field Table'),
    ('ndrcorepage', 'Page Table'),
    ('ndrcorevalue', 'Settings Table'),
    ('ndrcoresearchconfiguration', 'Search Configuration Table'),
    ('ndrcoreimage', 'Image Table'),
    ('ndrcoreuielementitem', 'UI Element Table'),
)
"""Tables which contain translatable fields."""


def get_available_languages():
    """Returns a list of available languages."""

    languages = NdrCoreValue.get_or_initialize(value_name='available_languages',
                                               init_value='',
                                               init_label='Available Languages',
                                               init_type=NdrCoreValue.ValueType.MULTI_LIST).get_value()

    available_languages = []
    for lang in languages:
        info = get_language_info(lang)
        available_languages.append((lang, info['name_local']))

    return available_languages


class TranslatableMixin:
    """Mixin which provides methods to translate translatable fields.
    All text values in the configuration are saved in a primary language.
    Database fields with translatable values have corresponding entries in
    the NdrCoreTranslation table."""

    translatable_fields = []
    """Fields which are translatable for the model this mixin is used with. """

    def translated_field(self, orig_value, field_name, object_id):
        """Returns the translated field for a given language. If no translation exists,
        the default value is returned. """
        try:
            translation = NdrCoreTranslation.objects.get(language=get_language(),
                                                         table_name=self._meta.model_name,
                                                         field_name=field_name,
                                                         object_id=object_id)
            if translation.translation != '':
                return translation.translation
            return orig_value
        except NdrCoreTranslation.DoesNotExist:
            return orig_value

    def save_translation(self, field_name, object_id, language, translation):
        """Saves a translation for a given field. """
        try:
            translation = NdrCoreTranslation.objects.get(language=language,
                                                         table_name=self._meta.model_name,
                                                         field_name=field_name,
                                                         object_id=object_id)
            translation.translation = translation
            translation.save()
        except NdrCoreTranslation.DoesNotExist:
            translation = NdrCoreTranslation(language=language,
                                             table_name=self._meta.model_name,
                                             field_name=field_name,
                                             object_id=self.id,
                                             translation=translation)
            translation.save()


class NdrCoreResultField(TranslatableMixin, models.Model):
    """An NdrCoreResultField is part of the display of a search result. Multiple result fields
    can be combined to a result card. Each result field has a type (see FieldType) which determines
    how the field is displayed. The expression (or rich_expression) is formed by mixing static text
    with data from the result.
    Example:
        The data provides a field 'person'. Its value is an object containing the fields 'first_name'
        and 'last_name'. The expression is 'Hello {person[first_name]} {person[last_name]}!'. The result
        field will display the text 'Hello John Doe!' if the data contains the fields 'person.first_name'
        and 'person.last_name'."""
    label = models.CharField(max_length=100,
                             blank=True, default='',
                             help_text="The label of the result field")

    rich_expression = RichTextUploadingField(null=True, blank=True,
                                             help_text='Rich text for your expression')
    """The expression to display. This can be a static text or a template string which is filled with data from the
    result. Rich text can be styled (bold, italic, etc.)"""

    field_classes = models.CharField(max_length=100, blank=True, default='',
                                     help_text="Bootstrap classes to apply to the display.")

    def __getattribute__(self, item):
        """Returns the translated field for a given language. If no translation exists,
        the default value is returned. """
        if item in ['rich_expression']:
            return self.translated_field(super().__getattribute__(item), item, str(self.id))
        return super().__getattribute__(item)

    def __str__(self):
        if self.label != '':
            return f'{self.label}'
        return f'{self.rich_expression}'


class NdrCoreSearchField(TranslatableMixin, models.Model):
    """A NdrCoreSearch field serves two purposes: First it can produce an HTML form field and second its information
      is used to formulate an API request."""

    class FieldType(models.IntegerChoices):
        """The FieldType of a searchField is used to render the HTML
        form and to determine the type of the API request."""

        STRING = 1, "String"
        """This type produces a text field"""

        NUMBER = 2, "Number"
        """This type produces a number field"""

        LIST = 3, "Dropdown List"
        """This field produces a dropdown list"""

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

        BOOLEAN_LIST = 11, "Boolean List"
        """This type produces a list of checkboxes"""

        __empty__ = 'Select a Type'

    field_name = models.CharField(max_length=100,
                                  primary_key=True,
                                  help_text="Choose a name for the field. Can't contain spaces or special characters"
                                            "and must be unique in your installation. Keep it short.")
    """The field_name is used as the HTML form name. This value is translatable."""

    field_label = models.CharField(max_length=100,
                                   help_text="This is the form field's label. It is shown to the user. "
                                             "This value is translatable.")
    """The field_label is the label for the HTML form field"""

    field_type = models.PositiveSmallIntegerField(choices=FieldType.choices,
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
                                     help_text="The name of the API parameter which is used to generate a query. "
                                               "If empty, the field_name is used.")
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

    text_choices = models.TextField(blank=True,
                                    default='',
                                    help_text="Used for infor text")

    list_condition = models.CharField(max_length=10, blank=True, default='OR',
                                      choices=(('OR', 'OR - Either in the selection'),
                                               ('AND', 'AND - All in the selection'),
                                               ('CHOOSE', 'CHOOSE - Let the user decide')),
                                      help_text="Condition for multiple list values")
    """Condition for multiple list values"""

    lower_value = models.CharField(null=True,
                                   blank=True,
                                   max_length=100,
                                   help_text="The lower value of a range field")
    """The lower value of a range field"""

    upper_value = models.CharField(null=True,
                                   blank=True,
                                   max_length=100,
                                   help_text="The upper value of a range field")
    """The upper value of a range field"""

    use_in_csv_export = models.BooleanField(default=False,
                                            help_text="Should this field be included in the CSV export?")
    """Should this field be included in the CSV export?"""

    initial_value = models.CharField(max_length=100,
                                     blank=True,
                                     default='',
                                     help_text="Initial value of the field. Refer to info box for valid values.")
    """Initial value of the field"""

    data_field_type = models.CharField(max_length=100,
                                       blank=True,
                                       default='',
                                       choices=(('int', 'Integer'), ('string', 'String')),
                                       help_text="Type of the field in the data source. This may change "
                                                 "the way data is queried.")

    input_transformation_regex = models.CharField(max_length=100,
                                                  blank=True,
                                                  default='',
                                                  help_text="Regex to transform the input value before "
                                                            "sending it to the API. {_value_} inserts the value.<br/> "
                                                            "(Example to convert a year to a date regex: '{_value_}-??-??')")

    def __getattribute__(self, item):
        """Returns the translated field for a given language. If no translation exists,
        the default value is returned. """
        if item in ['field_label', 'help_text']:
            return self.translated_field(super().__getattribute__(item), item, self.field_name)
        return super().__getattribute__(item)

    def is_choice_field(self):
        """Returns True if the field is a choice field. """
        if self.field_type in [self.FieldType.LIST, self.FieldType.MULTI_LIST, self.FieldType.BOOLEAN_LIST]:
            return True
        return False

    def is_multi_field(self):
        """Returns True if the field is a choice field. """
        if self.field_type in [self.FieldType.MULTI_LIST, self.FieldType.BOOLEAN_LIST]:
            return True
        return False

    def get_list_keys(self):
        """Returns the keys of the list choices. """
        if not self.is_choice_field():
            return []

        keys = [('key', ''),
                ('value', 'Undefined')]

        for lang in get_available_languages():
            keys.append((f'value_{lang[0]}', 'Undefined'))

        keys += [('initial', ''),
                 ('condition', True),
                 ('is_searchable', True),
                 ('is_printable', True)]

        for lang in get_available_languages():
            keys.append((f'info_{lang[0]}', ''))

        return keys

    def get_choices_list(self):
        if not self.is_choice_field():
            return []

        try:
            choice_json_list = json.loads(self.list_choices)
            for choice in choice_json_list:
                for key in self.get_list_keys():
                    if key[0] not in choice:
                        choice[key[0]] = key[1]

            return choice_json_list
        except json.JSONDecodeError as e:
            return []

    def get_choices_list_dict(self):
        json_list = self.get_choices_list()
        choices = {}
        for choice in json_list:
            choices[choice['key']] = choice
        return choices

    def get_choices(self, null_choice=False):
        json_list = self.get_choices_list()
        active_language = get_language()

        choices = []
        if null_choice:
            choices.append(('', 'Please Choose'))
        for choice in json_list:
            value = choice['value']
            if f'value_{active_language}' in choice:
                value = choice[f'value_{active_language}']
            choices.append((str(choice['key'])+'__'+str(choice['condition']).lower(), value))
        return choices

    def get_initial_value(self):
        """Returns the initial value of a search field. This is used to pre-fill the form with a value. """
        if self.field_type == self.FieldType.BOOLEAN:
            if self.initial_value == 'true':
                return True
            return False
        elif self.field_type == self.FieldType.BOOLEAN_LIST:
            choices = self.get_choices_list()   # TODO check
            self.initial_value = []
            for choice in choices:
                initial = choice.get('initial', 'false')
                condition = choice.get('condition', 'true')

                if initial == "true":
                    self.initial_value.append(choice['key'] + "__" + condition)

            return self.initial_value

        return self.initial_value

    def __str__(self):
        return f'{self.field_name} ({self.field_label})'


class NdrCoreResultFieldCardConfiguration(models.Model):
    """Result fields can be used in cards. In order to place them, they can be configured to fit in a grid with
     a NdrCoreResultFieldCardConfiguration."""

    result_field = models.ForeignKey(NdrCoreResultField,
                                     on_delete=models.CASCADE,
                                     help_text="The result field to place in a card")
    """The result field to place in a card"""

    field_row = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)],
                                    help_text="The row in the card. Starts with 1.",
                                    null=True)

    field_column = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)],
                                       help_text="The column in the card. Is a value between 1 and 12.",
                                       null=True)

    field_size = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)],
                                     help_text="The size of the field. Is a value between 1 and 12.",
                                     null=True)

    result_card_group = models.CharField(max_length=100,
                                         choices=(('normal', 'Normal'), ('compact', 'Compact')),
                                         default='normal',
                                         help_text="The group of the result card. Normal is the default group.")
    """The group of the result card. Normal is the default group."""


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

    connection_string_example = models.CharField(max_length=512, default='<connection-string>')
    """Example connection string. """

    supports_simple = models.BooleanField(default=True)
    """True if the API supports a catch all search with a simple search term. """

    supports_simple_and_or = models.BooleanField(default=True)
    """True if the API supports an AND and OR option for the simple search. """

    supports_advanced = models.BooleanField(default=True)
    """True if the API supports a field based search where different search values can be searched for different 
    fields."""

    supports_single_result = models.BooleanField(default=False)
    """True if a single result can be downloaded. """

    def __str__(self):
        return self.label


class NdrCoreSearchConfiguration(TranslatableMixin, models.Model):
    """ A search configuration describes a configured search. """

    # NAMES

    conf_name = models.CharField(verbose_name="Configuration Name",
                                 max_length=100,
                                 primary_key=True,
                                 help_text="Name of this search configuration. "
                                           "Can't contain spaces or special characters.")
    """Name of the search configuration. Can't contain spaces or special characters. Can't be 'simple'.
    Used as identifier."""

    conf_label = models.CharField(verbose_name="Configuration Label",
                                  max_length=100,
                                  unique=True,
                                  help_text="Label of this search configuration")
    """Label of the search configuration. This is the name which is displayed in the search form.
    This value is translatable."""

    # CONNECTION

    api_type = models.ForeignKey(NdrCoreApiImplementation, on_delete=models.CASCADE,
                                 verbose_name="API Type",
                                 help_text="Choose the API implementation of your configuration.")
    """Refers to the API implementation used for this configuration."""

    api_connection_url = models.CharField(null=False, blank=False,
                                          max_length=512,
                                          verbose_name="Connection URL",
                                          help_text="Connection URL for the API endpoint.")
    """Connection URL for the API endpoint. """

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

    # SEARCH

    search_form_fields = models.ManyToManyField(NdrCoreSearchFieldFormConfiguration,
                                                help_text="Fields associated with this configuration")
    """Fields associated with this configuration """

    search_id_field = models.CharField(max_length=100, blank=False, default='id',
                                       help_text="The ID field to identify an entry.")
    """The ID field to identify an entry. """

    sort_field = models.CharField(max_length=100, blank=False, default='id',
                                  help_text="The field to sort the result by.")
    """The field to sort the result by. """

    sort_order = models.CharField(max_length=100, blank=False, default='asc',
                                  choices=(('asc', 'Ascending'), ('desc', 'Descending')),
                                  help_text="The order to sort the result by.")
    """The order to sort the result by. """

    has_simple_search = models.BooleanField(default=True,
                                            help_text="Should this configuration feature a simple search?")
    """Should this configuration feature a simple search? """

    simple_search_first = models.BooleanField(default=True,
                                              help_text="Should the simple search be displayed first?")
    """Should the simple search be displayed first? """

    simple_query_main_field = models.CharField(max_length=100, blank=False, default='transcription.original',
                                               help_text="The main field to query for a simple search.")
    """The main field to query for a simple search. """

    simple_search_tab_title = models.CharField(max_length=100, blank=False, default='Simple Search',
                                               help_text="The title for the simple search tab.")
    """The title for the simple search tab. """

    simple_query_label = models.CharField(max_length=100, blank=False, default='Search',
                                          help_text="The label for the simple search field.")
    """The label for the simple search field. """

    simple_query_help_text = models.CharField(max_length=100, blank=False, default='Search the database',
                                              help_text="The help text for the simple search field.")
    """The help text for the simple search field. """

    # RESULT

    result_card_template = models.CharField(max_length=200,
                                            blank=False,
                                            default='default_template.html',
                                            help_text="The template to use for the result cards.")
    """The template to use for the result cards. """

    """The template to use for the result cards. """
    result_card_fields = models.ManyToManyField(NdrCoreResultFieldCardConfiguration,
                                                help_text="Result fields associated with this configuration")
    """Result fields associated with this configuration """

    search_has_compact_result = models.BooleanField(default=False,
                                                    help_text="If the result has a normal and a compact view, "
                                                              "check this box.")
    """If the result has a normal and a compact view, check this box."""

    compact_result_is_default = models.BooleanField(default=False,
                                                    help_text="If the compact result view is the default, "
                                                              "check this box.")
    """If the compact result view is the default, check this box."""

    page_size = models.IntegerField(default=10,
                                    verbose_name="Page Size",
                                    help_text="Size of the result page (e.g. 'How many results at once')")
    """The query results will return a page of the results. You can define the page size"""

    compact_page_size = models.IntegerField(default=10,
                                            verbose_name="Compact Page Size",
                                            help_text="Size of the compact result page (e.g. 'How many results at "
                                                      "once')")
    """The query results will return a page of the results. You can define the page size"""

    repository_url = models.URLField(default=None, null=True, blank=True,
                                     verbose_name="Repository URL",
                                     help_text="URL to the data repository where this data is stored.")
    """URL to the repository's website."""

    citation_expression = models.CharField(max_length=512, default=None, null=True, blank=True,
                                           verbose_name="Citation Expression",
                                           help_text="Expression to generate a citation for a result.")
    """Expression to generate a citation for a result."""

    manifest_relation_expression = models.CharField(max_length=512, default=None, null=True, blank=True,
                                                    verbose_name="Manifest Relation Expression",
                                                    help_text="Expression to generate a relation "
                                                              "to a manifest for a result.")
    """Expression to generate a relation to a manifest for a result."""

    manifest_page_expression = models.CharField(max_length=512, default=None, null=True, blank=True,
                                                verbose_name="Manifest Page Expression",
                                                help_text="Expression to generate a link to a page in a manifest.")
    """Expression to generate a link to a page in a manifest."""

    def __str__(self):
        return self.conf_name

    def __getattribute__(self, item):
        """Returns the translated field for a given language. If no translation exists,
        the default value is returned. """
        if item in ['conf_label', 'simple_search_tab_title', 'simple_query_label', 'simple_query_help_text']:
            return self.translated_field(super().__getattribute__(item), item, self.conf_name)
        return super().__getattribute__(item)


class NdrCorePage(TranslatableMixin, models.Model):
    """ An NdrCorePage is a web page on the ndr_core website instance. Each page has a type (see PageType) and upon
     creation, an HTML template is created and saved in the projects template folder. This allows users to create
     pages over the administration interface and then adapt its contents as needed."""

    class PageType(models.IntegerChoices):
        """Ndr Core can display multiple page types which are listed in this choice class """

        TEMPLATE = 1, "Template Page"
        """A template page is a static page. A HTML template is created which can be filled with any content"""

        SEARCH = 3, "Search Page"
        """A search page features a configured search form which contains a number of search fields"""

        CONTACT = 5, "Contact Form"
        """A contact from page displays a form to send a message to the project team"""

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
    """This is the name/title of the page. It will be displayed as a <h2>title</h2>. This value is translatable."""

    show_page_title = models.BooleanField(default=True,
                                          help_text="Should the page title be displayed?")
    """If this is set to False, the page title will not be displayed. """

    label = models.CharField(max_length=200,
                             help_text="The label of the page, e.g. the page's navigation label")
    """This is the navigation label which is displayed in the navigation. This value is translatable."""

    show_in_navigation = models.BooleanField(default=True,
                                             help_text="Should the page be displayed in the navigation?")
    """If this is set to False, the page will not be displayed in the navigation. """

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

    template_text = RichTextUploadingField(null=True, blank=True,
                                           help_text='Text for your template page')
    """Template Pages can be filled with RichText content (instead of 'manual' HTML). """

    parent_page = models.ForeignKey('NdrCorePage', null=True, blank=True, default=None, on_delete=models.DO_NOTHING,
                                    help_text="If you want this page to be a sub-page of another one, you can"
                                              "choose the parent page here")
    """Any NDR Core page might have children. Currently used for flip book. In the future to be used as navigation 
    hierarchy."""

    last_modified = models.DateTimeField(auto_now=True)
    """The last time the page was modified. """

    def __getattribute__(self, item):
        """Returns the translated field for a given language. If no translation exists,
        the default value is returned. """
        if item in ['name', 'label']:
            return self.translated_field(super().__getattribute__(item), item, str(self.id))
        return super().__getattribute__(item)

    def translated_template_text(self):
        """Returns the translated template_text for a given language.
        If no translation exists, the default template_text is returned. """
        try:
            translation = NdrCoreRichTextTranslation.objects.get(language=get_language(),
                                                                 table_name='NdrCorePage',
                                                                 field_name='template_text',
                                                                 object_id=str(self.id))
            if translation.translation != '':
                return translation.translation
            return self.template_text
        except NdrCoreRichTextTranslation.DoesNotExist:
            return self.template_text

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

    nav_link_color = ColorField(help_text='Color navigation for links.')
    """Color for hrefs."""

    nav_active_color = ColorField(help_text='Color for active navigation links.')
    """Color for hrefs."""

    tab_title_color = ColorField(help_text='Color for tab titles.')
    """Color for tab titles."""

    tab_active_title_color = ColorField(help_text='Color for active tab titles.')
    """Color for active tab titles."""

    form_field_bg = ColorField()
    """Background color of form fields."""

    form_field_fg = ColorField()
    """Foreground color of form fields."""

    footer_bg = ColorField()
    """Background color of the footer."""

    footer_link_color = ColorField()
    """Color of links in the footer."""

    footer_link_hover_color = ColorField()
    """Color of links in the footer."""

    powered_by_color = ColorField()
    """Color of the powered by text."""

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
        """Returns a list of all color fields. This is used to generate the colors.css file."""
        return ['background_color', 'container_bg_color', 'footer_bg', 'text_color', 'title_color',
                'button_color', 'button_text_color', 'button_hover_color', 'button_border_color',
                'second_button_color', 'second_button_text_color', 'second_button_hover_color',
                'second_button_border_color',
                'form_field_bg', 'form_field_fg',
                'footer_link_color', 'footer_link_hover_color', 'powered_by_color',
                'tab_title_color', 'tab_active_title_color',
                'link_color', 'nav_link_color', 'nav_active_color',
                'accent_color_1', 'accent_color_2', 'info_color', 'success_color', 'error_color']

    def __str__(self):
        return self.scheme_label


class NdrCoreValue(models.Model):
    """NdrCore provides a number of ready-to-use components which need to be configured with setting values. This data
     model stores these setting values. Example: A contact form has a subject field which can be prefilled with a string
     of choice. This string can be provided by this data model (value_name='contact_form_default_subject').
     The list of values is given and gets loaded from a fixture when the management command 'init_ndr_core' is
     executed. Users can only manipulate the 'value_value' of each object."""

    class ValueType(models.TextChoices):
        """NdrCoreValues can be of different types. The type determines how the value is displayed and how it can be
        manipulated. """
        STRING = "string", "String"
        RICH_STRING = "rich", "Rich Text"
        INTEGER = "integer", "Integer"
        BOOLEAN = "boolean", "Boolean"
        LIST = "list", "List"
        URL = "url", "URL"
        MULTI_LIST = "multi_list", "Multi List"

    value_name = models.CharField(max_length=100, primary_key=True,
                                  help_text='This is the identifier of a NdrCoreValue. '
                                            'Can\'t contain special characters.')
    """This is the identifier of a NdrCoreValue. In the source, each value gets loaded by searching for this name"""

    value_type = models.CharField(choices=ValueType.choices,
                                  max_length=10,
                                  help_text="The type of your value",
                                  default=ValueType.STRING)
    """The type of the value. This determines how the value is displayed and how it can be manipulated."""

    value_label = models.CharField(max_length=100,
                                   help_text='This is a human readable label for the value. '
                                             'It is used in the admin view forms.')
    """This is a human readable label for the value (e.g. its title)"""

    value_help_text = models.CharField(max_length=250,
                                       help_text='This is the help text of the form field.')
    """This is the help text for a value which explains to users what it is for"""

    value_value = models.CharField(max_length=100,
                                   help_text='This is the actual value which can be updated')
    """This is the actual value which can be updated by the user. This value is translatable."""

    value_options = models.CharField(max_length=200, default='',
                                     help_text='Used for value_type LIST and MULTI_LIST: comma-separated list')

    is_user_value = models.BooleanField(default=False)
    """Indicates if a value was created by a user"""

    is_translatable = models.BooleanField(default=False)
    """Indicates if a value can be translated"""

    def set_value(self, value):
        """Sets the value which is always saved as string as the proper type. """
        if self.value_type == NdrCoreValue.ValueType.BOOLEAN:
            if value:
                self.value_value = 'true'
            else:
                self.value_value = 'false'

    def get_value(self):
        """Returns the valued which is always saved as string as the proper type. """
        if self.value_type in [NdrCoreValue.ValueType.STRING,
                               NdrCoreValue.ValueType.RICH_STRING,
                               NdrCoreValue.ValueType.LIST,
                               NdrCoreValue.ValueType.URL]:
            return self.value_value
        if self.value_type == NdrCoreValue.ValueType.INTEGER:
            try:
                return int(self.value_value)
            except (TypeError, ValueError):
                return 0
        if self.value_type == NdrCoreValue.ValueType.BOOLEAN:
            if self.value_value.lower() == 'true' or self.value_value.lower() == 'on' or self.value_value == 'on':
                return True
            return False
        if self.value_type == NdrCoreValue.ValueType.MULTI_LIST:
            val = self.value_value.split(',')
            if val == ['']:
                return []
            return val

    def get_options(self):
        """For lists there are options, saved as string in the form: (key1,value1);(key2,value2)"""
        if self.value_type == NdrCoreValue.ValueType.LIST or self.value_type == NdrCoreValue.ValueType.MULTI_LIST:
            options = []
            option_tuples = self.value_options.split(";")
            for ot in option_tuples:
                ot = ot[1:-1]   # remove brackets
                spl = ot.split(',')
                options.append(spl)
            return options
        return None

    def translated_value(self):
        """Returns the translated field label for a given language. If no translation exists, the default label is
                returned. """

        try:
            translation = NdrCoreTranslation.objects.get(language=get_language(),
                                                         table_name='NdrCoreValue',
                                                         field_name='value_value',
                                                         object_id=self.value_name)
            if translation.translation != '':
                return translation.translation

            return self.value_value
        except NdrCoreTranslation.DoesNotExist:
            return self.value_value

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


class NdrCoreCorrection(models.Model):
    """Users can be given the opportunity to correct entries which have errors. Each correction can consist of
     multiple field corrections. Users need to provide an ORCID. This does not automatically correct data
     but administrators can accept or reject corrections."""

    corrected_dataset = models.ForeignKey(NdrCoreSearchConfiguration,
                                          on_delete=models.CASCADE)
    """The dataset which is corrected. """

    corrected_record_id = models.CharField(max_length=255)
    """The record ID of the corrected record. """

    corrector_orcid = models.CharField(max_length=50)
    """The ORCID of the corrector. """


class NdrCoreCorrectedField(models.Model):
    """A field correction is part of a correction. It consists of a field name, the old value and the new value. """

    ndr_correction = models.ForeignKey(NdrCoreCorrection,
                                       on_delete=models.CASCADE)
    """The correction which this field correction is part of. """

    field_name = models.CharField(max_length=100)
    """The field name which is corrected. """

    old_value = models.TextField()
    """The old value of the field. """

    new_value = models.TextField()
    """The new value of the field. """


class NdrCoreUserMessage(models.Model):
    """If the contact form is sent, a user message object is created. """

    message_subject = models.CharField(max_length=200)
    """The subject of the message. """

    message_text = models.TextField()
    """The text of the message. """

    message_time = models.DateTimeField(auto_now_add=True)
    """The time the message was sent. """

    message_ret_email = models.EmailField()
    """The e-mail address of the sender. """

    message_archived = models.BooleanField(default=False)
    """Indicates if the message has been archived. """

    message_forwarded = models.BooleanField(default=False)
    """Indicates if the message has been forwarded to a specified e-mail address. """

    def __str__(self):
        return f"{self.message_subject} (from: {self.message_ret_email})"


class NdrCoreSearchStatisticEntry(models.Model):
    """Every time a search is executed, a NdrCoreSearchStatisticEntry object is created if the setting
    'statistics_feature' is set to 'true' """

    search_config = models.ForeignKey(NdrCoreSearchConfiguration, on_delete=models.CASCADE)
    """The API which was queried in the search. """

    search_term = models.CharField(max_length=100, default='')
    """The search term(s) which have been searched. """

    search_query = models.CharField(max_length=255, default='')
    """The actual query which was sent to the API. """

    search_no_results = models.IntegerField(default=0)
    """The number of results which were returned. """

    search_time = models.DateTimeField(auto_now_add=True)
    """The time the user searched. """

    search_location = models.CharField(max_length=20, null=True)
    """The location the user searched from. """

    language = models.CharField(max_length=10, null=True, default=None,
                                blank=True,
                                help_text='Language of the search.')
    """Language of the search. """


class NdrCoreImage(models.Model, TranslatableMixin):
    """ Directory of all images used outside the ckeditor and the logo. """

    class ImageGroup(models.TextChoices):
        """Images are grouped into different groups."""
        PAGE_LOGOS = "page_logos", "Page Logos"
        BGS = "backgrounds", "Background Images"
        ELEMENTS = "elements", "Slideshow Images"
        FIGURES = "figures", "Figures"
        LOGOS = "logos", "Partner Images"
        PEOPLE = "people", "People"

        @staticmethod
        def get_label_by_value(group_value, choices):
            """Returns the label for a given value. """
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
                                   choices=ImageGroup.choices,
                                   help_text='Group the image belongs to.')
    """Group the image belongs to. """

    index_in_group = models.IntegerField(default=0)
    """For ordering the images within the group. """

    image_active = models.BooleanField(default=True)
    """To indicate that this image is not to be used in automatic collections."""

    language = models.CharField(max_length=10, null=True, default=None,
                                blank=True,
                                help_text='Language of the image.')
    """Language of the image. """

    def __getattribute__(self, item):
        """Returns the translated field for a given language. If no translation exists,
        the default value is returned. """
        if item in ['title', 'caption', 'citation']:
            return self.translated_field(super().__getattribute__(item), item, str(self.pk))
        return super().__getattribute__(item)

    def get_absolute_url(self):
        """Returns the absolute url of the image. """
        return reverse('ndr_core:view_images', kwargs={'group': self.image_group})

    def __str__(self):
        return self.title


class NdrCoreUpload(models.Model):
    """ Directory of all uploads. """

    title = models.CharField(max_length=200, blank=True, default='',
                             help_text='Title of the upload.')
    """Title of the upload"""

    file = models.FileField(upload_to='uploads/files/')
    """Actual file"""


class NdrCoreManifestGroup(TranslatableMixin, models.Model):
    """ Directory of all manifest groups. """

    title = models.CharField(max_length=200,
                             help_text='Title of the manifest group.')
    """Title of the manifest group."""

    order_value_1_title = models.CharField(max_length=200, blank=True, null=True, default=None,
                                           help_text='Order value 1 title')
    """Order value 1 title"""

    order_value_2_title = models.CharField(max_length=200, blank=True, null=True, default=None,
                                           help_text='Order value 2 title')
    """Order value 2 title"""

    order_value_3_title = models.CharField(max_length=200, blank=True, null=True, default=None,
                                           help_text='Order value 3 title')
    """Order value 3 title"""

    def __getattribute__(self, item):
        """Returns the translated field for a given language. If no translation exists,
        the default value is returned. """
        if item in ['title']:
            return self.translated_field(super().__getattribute__(item), item, str(self.pk))
        return super().__getattribute__(item)

    def __str__(self):
        return self.title


class NdrCoreManifest(TranslatableMixin, models.Model):
    """ Directory of all manifests. """

    identifier = models.CharField(max_length=200, primary_key=True,
                                  help_text='Identifier of the manifest. '
                                            'Is used to reference the manifest in the code.')
    """Identifier of the manifest. Is used to reference the manifest in the code."""

    title = models.CharField(max_length=200, blank=True, default='',
                             help_text='Title of the manifest. Is shown in the dropdown of the page.')
    """Title of the upload"""

    manifest_group = models.ForeignKey(NdrCoreManifestGroup, on_delete=models.CASCADE)
    """Group of the manifest"""

    file = models.FileField(upload_to='uploads/manifests/')
    """Actual file"""

    order_value_1 = models.CharField(max_length=200, blank=True, null=True, default=None)
    """Order value 1"""

    order_value_2 = models.CharField(max_length=200, blank=True, null=True, default=None)
    """Order value 2"""

    order_value_3 = models.CharField(max_length=200, blank=True, null=True, default=None)
    """Order value 3"""

    def __getattribute__(self, item):
        """Returns the translated field for a given language. If no translation exists,
        the default value is returned. """
        if item in ['title']:
            return self.translated_field(super().__getattribute__(item), item, str(self.pk))
        return super().__getattribute__(item)

    def __str__(self):
        return self.title


class NdrCoreUIElement(models.Model):
    """ UI Element """

    class UIElementType(models.TextChoices):
        """NDR Core UI Element types."""
        CARD = "card", "Card"
        SLIDESHOW = "slides", "Slideshow"
        CAROUSEL = "carousel", "Carousel"
        JUMBOTRON = "jumbotron", "Jumbotron"
        IFRAME = "iframe", "IFrame"
        BANNER = "banner", "Banner"
        MANIFEST_VIEWER = "manifest_viewer", "Manifest Viewer"

    type = models.CharField(max_length=100,
                            choices=UIElementType.choices,
                            help_text='Type of the element. Decides how it is rendered. ')
    """Type of the element. Decides how it is rendered. """

    name = models.CharField(primary_key=True,
                            max_length=100,
                            help_text='Name of the element for your reference.')
    """Name and primary key of the element. """

    show_indicators = models.BooleanField(default=False,
                                          help_text='Show the indicators for slideshows and carousels?')
    """Show the indicators for slideshows and carousels? (Applies to: Slideshow, Carousel)"""

    autoplay = models.BooleanField(default=False,
                                   help_text='Autoplay carousels and slideshows?')
    """Autoplay carousels and slideshows? """

    def items(self):
        """Returns the items of the UI element, ordered. """
        return self.ndrcoreuielementitem_set.all().order_by('order_idx')

    def get_absolute_url(self):
        """Returns the absolute url of the image."""
        return reverse('ndr_core:view_ui_element', kwargs={'pk': self.pk})


class NdrCoreUiElementItem(models.Model, TranslatableMixin):
    """UI Element Item. Is part of a UI Element. """

    belongs_to = models.ForeignKey(NdrCoreUIElement, on_delete=models.CASCADE)
    """The UI Element this item belongs to. """

    order_idx = models.IntegerField()
    """The order index of the item. """

    ndr_image = models.ForeignKey(NdrCoreImage, on_delete=models.CASCADE, null=True)
    """The image of the item. """

    title = models.CharField(max_length=100, blank=True)
    """The title of the item. """

    text = models.TextField(blank=True)
    """The text of the item. """

    url = models.URLField(blank=True)
    """The url of the item. """

    manifest_group = models.ForeignKey(NdrCoreManifestGroup, on_delete=models.CASCADE, null=True)
    """The manifest group of the item. """

    def __getattribute__(self, item):
        """Returns the translated field for a given language. If no translation exists,
        the default value is returned. """
        if item in ['title', 'text']:
            return self.translated_field(super().__getattribute__(item), item, str(self.pk))
        return super().__getattribute__(item)


class NdrCoreTranslation(models.Model):
    """NdrCoreTranslation is used to translate CharField fields."""

    language = models.CharField(max_length=10)
    """Language of the translation. """

    table_name = models.CharField(max_length=100, choices=TRANSLATABLE_TABLES)
    """Name of the table the field belongs to. """

    object_id = models.CharField(max_length=100)
    """ID of the object the field belongs to. """

    field_name = models.CharField(max_length=100)
    """Name of the field to translate. """

    translation = models.CharField(max_length=255)
    """Translation of the field. """


class NdrCoreRichTextTranslation(models.Model):
    """NdrCoreRichTextTranslation is used to translate rich text fields."""

    language = models.CharField(max_length=10)
    """Language of the translation. Should be a language returned by get_available_languages(). """

    table_name = models.CharField(max_length=100, choices=TRANSLATABLE_TABLES)
    """Name of the table the field belongs to.  """

    object_id = models.CharField(max_length=100)
    """ID of the object the field belongs to. """

    field_name = models.CharField(max_length=100)
    """Name of the field to translate. """

    translation = RichTextUploadingField(null=True, blank=True,
                                         help_text='Text for your template page')
    """Template Pages can be filled with RichText content (instead of 'manual' HTML). """
