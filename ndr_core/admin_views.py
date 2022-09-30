from django.shortcuts import render
from django.views import View
from django.views.generic import ListView

from ndr_core.models import NdrCorePage


class ManagePages(ListView):

    model = NdrCorePage
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
