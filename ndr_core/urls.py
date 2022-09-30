from django.urls import path

from ndr_core.admin_views import ManagePages

app_name = 'ndr_core'
urlpatterns = [
    path('manage/', ManagePages.as_view(), name='manage_pages'),
]