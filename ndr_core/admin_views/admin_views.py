"""Contains basic views used in the NDRCore admin interface."""
from datetime import datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django_filters import FilterSet
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from ndr_core.models import NdrCoreValue, \
    NdrCoreSearchStatisticEntry, NdrCoreUserMessage
from ndr_core.admin_tables import StatisticsTable


class NdrCoreDashboard(LoginRequiredMixin, View):
    """The NDR Core dashboard is the start page of the admin interface. It shows your pages and your options. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        return render(self.request,
                      template_name='ndr_core/admin_views/overview/dashboard.html',
                      context={'new_messages': NdrCoreUserMessage.objects.filter(message_archived=False).count(),
                               'total_searches': NdrCoreSearchStatisticEntry.objects.all().count()})


class HelpView(LoginRequiredMixin, View):
    """TODO """
    def get(self, request, *args, **kwargs):
        chapter = None
        if "chapter" in kwargs:
            chapter = kwargs["chapter"]
        return render(self.request,
                      template_name='ndr_core/admin_views/overview/help.html',
                      context={'chapter': chapter})


class StatisticsFilter(FilterSet):
    class Meta:
        model = NdrCoreSearchStatisticEntry
        fields = {"search_query": ["contains"]}

class StatisticsView(LoginRequiredMixin, SingleTableMixin, FilterView):
    """TODO """
    table_class = StatisticsTable
    model = NdrCoreSearchStatisticEntry
    template_name = 'ndr_core/admin_views/overview/view_statistics.html'
    paginate_by = 25

    filterset_class = StatisticsFilter

    def get_context_data(self, **kwargs):
        context = super(StatisticsView, self).get_context_data(**kwargs)
        today = datetime.today().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
        first_of_week = today - timedelta(days=today.weekday())
        first_of_month = today.replace(day=1)
        first_of_year = today.replace(day=1, month=1)

        context['statistics_enabled'] = NdrCoreValue.objects.get(value_name='statistics_feature').get_value()
        context['search_summary'] = {
            'today': NdrCoreSearchStatisticEntry.objects.filter(search_time__gte=first_of_week).count(),
            'this_week': NdrCoreSearchStatisticEntry.objects.filter(search_time__gte=first_of_week).count(),
            'this_month': NdrCoreSearchStatisticEntry.objects.filter(
                search_time__gte=first_of_month).count(),
            'this_year': NdrCoreSearchStatisticEntry.objects.filter(search_time__gte=first_of_year).count(),
            'total': NdrCoreSearchStatisticEntry.objects.all().count()}
        return context

    def get_queryset(self):
        return NdrCoreSearchStatisticEntry.objects.all().order_by('-search_time')


def set_statistics_option(request, option):
    value = NdrCoreValue.objects.get(value_name='statistics_feature')
    value.value_value = option
    value.save()
    return redirect('ndr_core:search_statistics')
