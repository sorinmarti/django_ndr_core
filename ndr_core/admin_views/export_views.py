""" Views to export the settings of the NDR Core App """
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import redirect

from ndr_core.models import NdrCoreColorScheme, NdrCoreValue, NdrCoreUserMessage


@login_required
def export_color_palette(request, pk):
    """Exports a color palette as JSON. """

    try:
        ndr_object = NdrCoreColorScheme.objects.get(pk=pk)
        data = serializers.serialize("json", [ndr_object])
        data_json = json.loads(data)
        return JsonResponse(data_json[0])
    except NdrCoreColorScheme.DoesNotExist:
        messages.error(request, 'Color Palette not Found')
        return redirect('ndr_core:configure_colors')


@login_required
def export_settings(request):
    """Exports the settings as JSON. """

    ndr_object = NdrCoreValue.objects.all()
    data = serializers.serialize("json", ndr_object)
    data_json = json.loads(data)
    return JsonResponse(data_json, safe=False)


@login_required
def export_messages(request):
    """Exports the messages as JSON. """
    ndr_object = NdrCoreUserMessage.objects.all()
    data = serializers.serialize("json", ndr_object)
    data_json = json.loads(data)
    return JsonResponse(data_json, safe=False)
