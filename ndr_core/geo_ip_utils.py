"""Module for getting geolocation from IP address."""
from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError


def get_user_ip(request):
    """Get user IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_geolocation(ip):
    """Get geolocation from IP address."""
    g = GeoIP2()
    try:
        c = g.country(ip)
        return c
    except AddressNotFoundError:
        return None
