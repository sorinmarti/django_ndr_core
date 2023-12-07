"""Views for the correction feature. """
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.models import NdrCoreValue


class ConfigureCorrections(AdminViewMixin, LoginRequiredMixin, View):
    """View to add/edit/delete Corrections. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        correction_enabled = False
        if NdrCoreValue.objects.get(value_name='correction_feature').value_value == "true":
            correction_enabled = True

        context = {'correction_enabled': correction_enabled}
        return render(self.request, template_name='ndr_core/admin_views/overview/configure_corrections.html',
                      context=context)


@login_required
def set_correction_option(request, option):
    """Sets the correction option to the given value. """
    value = NdrCoreValue.objects.get(value_name='correction_feature')
    value.value_value = option
    value.save()
    return redirect('ndr_core:configure_corrections')
