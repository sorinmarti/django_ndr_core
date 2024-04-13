from django.urls import path

from ndr_core.views import dispatch, display_schema_or_404, google_search_console_verification_view
from ndr_core.ndr_settings import NdrSettings

app_name = NdrSettings.APP_NAME

urlpatterns = [
    path('', dispatch, name='index'),
    path('schemas/<str:schema_name>', display_schema_or_404, name='display_schema'),
    path('p/<str:ndr_page>/', dispatch, name='ndr_view'),

    path('robots.txt', dispatch, name='robots'),
    path('sitemap.xml', dispatch, name='sitemap'),
    path('google<str:verification_file>.html', google_search_console_verification_view),
]
