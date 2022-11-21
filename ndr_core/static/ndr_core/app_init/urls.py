from django.urls import path

from ndr_core.models import NdrCorePage
from ndr_core.views import dispatch, NdrTemplateView, NdrTestView
from ndr_core.ndr_settings import NdrSettings

app_name = NdrSettings.APP_NAME
urlpatterns = [
    path('', NdrTemplateView.as_view(template_name=f'{app_name}/index.html',
                                     ndr_page=NdrCorePage.objects.get(view_name='index')), name='index'),
    path('p/<str:ndr_page>/', dispatch, name='ndr_view'),

    # Test page to test UI settings
    path('test/ui/settings/', NdrTestView.as_view(), name='test_ui_settings'),
]