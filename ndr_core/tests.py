from django.test import TestCase

from ndr_core.api.mongodb.mongodb_query import MongoDBQuery
from ndr_core.models import NdrCorePage, NdrCoreApiConfiguration, NdrCoreSearchField, \
    NdrCoreSearchConfiguration, NdrCoreSearchFieldFormConfiguration, NdrCoreApiImplementation
from ndr_core.api_factory import ApiFactory

class TestMongoDBApi(TestCase):

    def setUp(self):
        api_type = NdrCoreApiImplementation.objects.create(name="mongodb")
        api_conf = NdrCoreApiConfiguration.objects.create(api_name='mongodb_test',
                                                          api_type=api_type,
                                                          api_host='localhost',
                                                          api_protocol=NdrCoreApiConfiguration.Protocol.HTTP,
                                                          api_port=27017,
                                                          api_label='MongoDB Test',
                                                          api_page_size=10)

    def test_mongodb_api(self):
        api_conf = NdrCoreApiConfiguration.objects.get(api_name='mongodb_test')
        query = MongoDBQuery(api_conf)
        simple = query.get_simple_query('Singer')

        query.set_value('name', 'John')
        advanced = query.get_advanced_query()

        print(simple)
        print(advanced)

class SearchConfigurationTestCase(TestCase):

    def setUp(self):
        api_type = NdrCoreApiImplementation.objects.create(name="ndr_core")

        api_conf = NdrCoreApiConfiguration.objects.create(api_name='asia_dir',
                                                          api_type=api_type,
                                                          api_host='asiadir.int',
                                                          api_protocol=NdrCoreApiConfiguration.Protocol.HTTP,
                                                          api_port=8080,
                                                          api_label='Asia Directories',
                                                          api_page_size=15)

        field_1 = NdrCoreSearchField.objects.create(field_name='first_name',
                                                    field_label='First Name(s)',
                                                    field_type=NdrCoreSearchField.FieldType.STRING,
                                                    field_required=False,
                                                    help_text='Our database only has initials',
                                                    api_parameter='givenname')

        field_2 = NdrCoreSearchField.objects.create(field_name='last_name',
                                                    field_label='Last Name',
                                                    field_type=NdrCoreSearchField.FieldType.STRING,
                                                    field_required=False,
                                                    help_text='Enter a name',
                                                    api_parameter='surname')

        field_1_conf = NdrCoreSearchFieldFormConfiguration.objects.create(search_field=field_1,
                                                                          field_row=0,
                                                                          field_column=0,
                                                                          field_size=8)

        field_2_conf = NdrCoreSearchFieldFormConfiguration.objects.create(search_field=field_2,
                                                                          field_row=0,
                                                                          field_column=1,
                                                                          field_size=4)

        search_conf = NdrCoreSearchConfiguration.objects.create(api_configuration=api_conf)
        search_conf.search_form_fields.add(field_1_conf)
        search_conf.search_form_fields.add(field_2_conf)
        search_conf.save()

    def test_api_configuration(self):
        conf = NdrCoreSearchConfiguration.objects.get(api_configuration__api_name="asia_dir")
        self.assertIsNotNone(conf)
        self.assertIsNotNone(conf.api_configuration)

    def test_basic_query(self):
        conf = NdrCoreSearchConfiguration.objects.get(api_configuration__api_name="asia_dir")
        query = ApiFactory(conf.api_configuration).get_query_class()(conf.api_configuration, page=1)
        query_string = query.get_simple_query('1234')
        self.assertEqual('http://asiadir.int:8080/query/basic?s=15&p=1&t=1234', query_string)

    def test_advanced_query(self):
        conf = NdrCoreSearchConfiguration.objects.get(api_configuration__api_name="asia_dir")
        query = ApiFactory(conf.api_configuration).get_query_class()(conf.api_configuration, page=1)
        query.set_value("first_name", "John")
        query.set_value("last_name", "Smith")
        query_string = query.get_advanced_query()
        self.assertEqual('http://asiadir.int:8080/query/advanced?s=15&p=1&givenname=John&surname=Smith', query_string)


class PagesTestCase(TestCase):

    def setUp(self):
        NdrCorePage.objects.create(name='Welcome Home',
                                   label='Home',
                                   view_name='home',
                                   nav_icon='fas-fa home',
                                   index=0)

    def test_pages(self):
        # TODO This test is useless
        page = NdrCorePage.objects.get(view_name='home')
        # This will return /p/home/ when ndr app is available or '#' if not.
        # self.assertEqual('#', page.url())


class ResultTemplateTestCase(TestCase):

    def test_template(self):
        pass