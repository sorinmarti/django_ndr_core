from django.urls import path
from django.views.generic import TemplateView

from ndr_core.views import dispatch
from ndr_core.ndr_settings import NdrSettings

app_name = NdrSettings.APP_NAME
urlpatterns = [
    path('', TemplateView.as_view(template_name=f'{app_name}/index.html'), name='index'),
    path('p/<str:ndr_page>/', dispatch, name='ndr_view'),
]