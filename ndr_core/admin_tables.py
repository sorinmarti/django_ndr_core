"""Admin tables for ndr_core. Only the search statistics table is used."""
import django_tables2 as tables
from ndr_core.models import NdrCoreSearchStatisticEntry


default_table_attrs = {"class": "table table-sm table-hover table-bordered",
                       'th': {'style': 'text-align: left; padding-left: 20px;'},
                       'td': {'style': 'text-align: left; padding-left: 20px;'}}
default_row_attrs = {'data-href': lambda record: record.get_absolute_url}


class StatisticsTable(tables.Table):    # pylint: disable=too-few-public-methods
    """Shows a list of searches made by guests."""

    class Meta:    # pylint: disable=too-few-public-methods
        """Metaclass for StatisticsTable."""
        template_name = "ndr_core/admin_views/bootstrap4-responsive.html"
        attrs = default_table_attrs
        model = NdrCoreSearchStatisticEntry
        fields = ("search_api", "search_term", "search_query", "search_no_results", "search_time")
