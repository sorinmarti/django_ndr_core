import json

from django.contrib import messages
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import redirect

from ndr_core.models import NdrCoreColorScheme, NdrCoreValue, NdrCoreUserMessage


def export_color_palette(request, pk):
    """TODO """

    try:
        ndr_object = NdrCoreColorScheme.objects.get(pk=pk)
        data = serializers.serialize("json", [ndr_object])
        data_json = json.loads(data)
        return JsonResponse(data_json[0])
    except NdrCoreColorScheme.DoesNotExist:
        messages.error(request, 'Color Palette not Found')
        return redirect('ndr_core:configure_colors')


def export_settings(request):
    """TODO """
    ndr_object = NdrCoreValue.objects.all()
    data = serializers.serialize("json", ndr_object)
    data_json = json.loads(data)
    return JsonResponse(data_json, safe=False)


def export_messages(request):
    """TODO """
    ndr_object = NdrCoreUserMessage.objects.all()
    data = serializers.serialize("json", ndr_object)
    data_json = json.loads(data)
    return JsonResponse(data_json, safe=False)
