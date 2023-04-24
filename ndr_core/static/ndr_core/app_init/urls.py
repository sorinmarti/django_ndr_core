from django.urls import path

from ndr_core.views import dispatch, NdrTestView
from ndr_core.ndr_settings import NdrSettings

app_name = NdrSettings.APP_NAME

urlpatterns = [
    path('', dispatch, name='index'),
    path('p/<str:ndr_page>/', dispatch, name='ndr_view'),

    # Test page to test UI settings
    path('test/ui/settings/', NdrTestView.as_view(), name='test_ui_settings'),
]