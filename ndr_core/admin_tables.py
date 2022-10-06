import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import mark_safe

from ndr_core.models import NdrCorePage, SearchConfiguration, NdrCoreValue, NdrSearchField, ApiConfiguration
from ndr_core.ndr_settings import NdrSettings


class PagesTable(tables.Table):
    class Meta:
        model = NdrCorePage
        fields = ('name', 'label', 'page_type', 'view_name')


class PagesManageTable(PagesTable):

    option_column = tables.Column(verbose_name='Options', accessor='id')

    class Meta(PagesTable.Meta):
        pass

    @staticmethod
    def render_option_column(value, record):
        return mark_safe('<a href="'+reverse('ndr_core:edit_page', kwargs={'pk': value})+'" class="btn btn-sm btn-primary">Edit</a>'
                         '&nbsp;'
                         '<a href="'+reverse('ndr_core:delete_page', kwargs={'pk': value})+'" class="btn btn-sm btn-danger">Delete</a>'
                         '&nbsp;'
                         '<a href="'+reverse('ndr_core:move_page_up', kwargs={'pk': value})+'" class="btn btn-sm btn-primary">Up</a>'
                         '&nbsp;'
                         '<a href="'+reverse(f'{NdrSettings.APP_NAME}:ndr_view', kwargs={'ndr_page': record.view_name})+'" class="btn btn-sm btn-secondary">View</a>')


class FormsTable(tables.Table):
    class Meta:
        model = SearchConfiguration


class SearchFieldTable(tables.Table):
    class Meta:
        model = NdrSearchField


class SettingsTable(tables.Table):
    value_value = tables.Column(accessor='id')

    class Meta:
        model = NdrCoreValue
        fields = ('value_label', 'value_help_text', 'value_value')

    @staticmethod
    def render_value_value(value, record):
        return record.value_value


class ChangeSettingsTable(SettingsTable):
    class Meta(SettingsTable.Meta):
        pass

    @staticmethod
    def render_value_value(value, record):
        return mark_safe(f'<input type="text" name="save_{record.value_name}" value="{record.value_value}" />')


class ApiTable(tables.Table):

    class Meta:
        model = ApiConfiguration
        fields = ('api_name', 'api_host', 'api_protocol', 'api_port', 'api_label', 'api_page_size')