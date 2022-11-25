from django.urls import path

from ndr_core.models import NdrCorePage
from ndr_core.views import dispatch, NdrTemplateView, NdrTestView, NdrDownloadView
from ndr_core.ndr_settings import NdrSettings

app_name = NdrSettings.APP_NAME

try:
    index_page = NdrCorePage.objects.get(view_name='index')
except NdrCorePage.DoesNotExist:
    index_page = None

urlpatterns = [
    path('', NdrTemplateView.as_view(template_name=f'{app_name}/index.html',
                                     ndr_page=index_page), name='index'),
    path('p/<str:ndr_page>/', dispatch, name='ndr_view'),

    # Download URL for single DB entry
    path('download/<str:api_config>/<str:record_id>/', NdrDownloadView.as_view(), name='download_record'),

    # Test page to test UI settings
    path('test/ui/settings/', NdrTestView.as_view(), name='test_ui_settings'),
]