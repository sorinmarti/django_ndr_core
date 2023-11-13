"""
URL configuration for django_ndr_core project.
"""
from django.contrib import admin
from django.urls import path
from ndr_core.ndr_settings import NdrSettings

urlpatterns = [
    path("admin/", admin.site.urls),
]
urlpatterns += NdrSettings.get_urls()