from django.test import TestCase

from ndr_core.models import NdrCorePage, ApiConfiguration, NdrSearchField, \
    SearchConfiguration, SearchFieldFormConfiguration
from ndr_core.query import Query


class SearchConfigurationTestCase(TestCase):

    def setUp(self):
        api_conf = ApiConfiguration.objects.create(api_name='asia_dir',
                                                   api_host='asiadir.int',
                                                   api_protocol=ApiConfiguration.Protocol.HTTP,
                                                   api_port=8080,
                                                   api_label='Asia Directories',
                                                   api_page_size=15)

        field_1 = NdrSearchField.objects.create(field_name='first_name',
                                                field_label='First Name(s)',
                                                field_type=NdrSearchField.FieldType.STRING,
                                                field_required=False,
                                                help_text='Our database only has initials',
                                                api_parameter='givenname')

        field_2 = NdrSearchField.objects.create(field_name='last_name',
                                                field_label='Last Name',
                                                field_type=NdrSearchField.FieldType.STRING,
                                                field_required=False,
                                                help_text='Enter a name',
                                                api_parameter='surname')

        field_1_conf = SearchFieldFormConfiguration.objects.create(search_field=field_1,
                                                                   field_row=0,
                                                                   field_column=0,
                                                                   field_size=8)

        field_2_conf = SearchFieldFormConfiguration.objects.create(search_field=field_2,
                                                                   field_row=0,
                                                                   field_column=1,
                                                                   field_size=4)

        search_conf = SearchConfiguration.objects.create(api_configuration=api_conf)
        search_conf.search_form_fields.add(field_1_conf)
        search_conf.search_form_fields.add(field_2_conf)
        search_conf.save()

    def test_api_configuration(self):
        conf = SearchConfiguration.objects.get(api_configuration__api_name="asia_dir")
        self.assertIsNotNone(conf)
        self.assertIsNotNone(conf.api_configuration)

    def test_basic_query(self):
        query = Query("asia_dir")
        query_string = query.get_simple_query('1234', 1)
        self.assertEqual('http://asiadir.int:8080/query/basic?s=15&p=1&t=1234', query_string)

    def test_advanced_query(self):
        query = Query("asia_dir")
        query.set_value("first_name", "John")
        query.set_value("last_name", "Smith")
        query_string = query.get_advanced_query(1)
        self.assertEqual('http://asiadir.int:8080/query/advanced?s=15&p=1&givenname=John&surname=Smith', query_string)


class PagesTestCase(TestCase):

    def setUp(self):
        NdrCorePage.objects.create(name='Welcome Home',
                                   label='Home',
                                   view_name='home',
                                   nav_icon='fas-fa home',
                                   index=0)

    def test_pages(self):
        page = NdrCorePage.objects.get(view_name='home')
        self.assertEqual('#', page.url())

