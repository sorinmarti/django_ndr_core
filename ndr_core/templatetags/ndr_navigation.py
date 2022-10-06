from django import template

from ndr_core.models import NdrCorePage

register = template.Library()


@register.inclusion_tag('ndr_core/navigation/navigation.html')
def print_navigation():
    navigation = NdrCorePage.objects.all().order_by('index')
    return {'navigation': navigation}


@register.inclusion_tag('ndr_core/navigation/navigation_bottom.html')
def print_navigation_bottom():
    navigation = NdrCorePage.objects.all().order_by('index')
    return {'navigation': navigation}
