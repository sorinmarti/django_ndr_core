from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from ndr_core.admin_forms import NdrCoreLoginForm
from ndr_core.admin_views import create_search_fields, PageEditView, PageDeleteView, move_page_up, \
    ConfigureSettings, ApiConfigurationCreateView, ApiConfigurationEditView, SearchConfigurationCreateView, \
    SearchConfigurationEditView, SearchConfigurationDeleteView, SearchFieldConfigurationCreateView, \
    SearchFieldConfigurationEditView, SearchFieldConfigurationDeleteView, ApiConfigurationDeleteView, preview_image, \
    ConfigureUI
from ndr_core.admin_views import NdrCoreDashboard, ManagePages, ConfigureApi, ConfigureSearch, ConfigureSearchFields, \
    PageCreateView
from ndr_core.views import ApiTestView, NdrDownloadView

app_name = 'ndr_core'
urlpatterns = [
    path('', NdrCoreDashboard.as_view(), name='dashboard'),

    # PAGES
    path('configure/pages/', ManagePages.as_view(), name='configure_pages'),
    path('configure/pages/create/new/', PageCreateView.as_view(), name='create_page'),
    path('configure/pages/edit/<int:pk>/', PageEditView.as_view(), name='edit_page'),
    path('configure/pages/delete/<int:pk>/', PageDeleteView.as_view(), name='delete_page'),
    path('configure/pages/move/up/<int:pk>/', move_page_up, name='move_page_up'),

    # SETTINGS
    path('configure/settings/', ConfigureSettings.as_view(), name='configure_settings'),
    path('configure/ui_settings/', ConfigureUI.as_view(), name='ui_settings'),

    # API
    path('configure/api/', ConfigureApi.as_view(), name='configure_api'),
    path('configure/api/create/new/', ApiConfigurationCreateView.as_view(), name='create_api'),
    path('configure/api/edit/<int:pk>/', ApiConfigurationEditView.as_view(), name='edit_api'),
    path('configure/api/delete/<int:pk>/', ApiConfigurationDeleteView.as_view(), name='delete_api'),

    # SEARCH CONFIG
    path('configure/search/', ConfigureSearch.as_view(), name='configure_search'),
    path('configure/search/create/new/', SearchConfigurationCreateView.as_view(), name='create_search'),
    path('configure/search/edit/<int:pk>/', SearchConfigurationEditView.as_view(), name='edit_search'),
    path('configure/search/delete/<int:pk>/', SearchConfigurationDeleteView.as_view(), name='delete_search'),
    path('configure/search/image/preview/<str:img_config>/', preview_image, name='preview_image'),

    # SEARCH FIELDS
    path('configure/search/fields/', ConfigureSearchFields.as_view(), name='configure_search_fields'),
    path('configure/search/fields/create/new/', SearchFieldConfigurationCreateView.as_view(), name='create_search_field'),
    path('configure/search/fields/edit/<int:pk>/', SearchFieldConfigurationEditView.as_view(), name='edit_search_field'),
    path('configure/search/fields/delete/<int:pk>/', SearchFieldConfigurationDeleteView.as_view(), name='delete_search_field'),
    path('configure/search/fields/schema/<int:schema_pk>/', create_search_fields, name='create_fields_from_schema'),

    # Login / Logout
    path('login/', auth_views.LoginView.as_view(template_name='ndr_core/admin_views/login.html',
                                                form_class=NdrCoreLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='ndr_core/admin_views/logout.html'), name='logout'),

    # Help
    path('help/', TemplateView.as_view(template_name='ndr_core/admin_views/help.html'), name='help'),

    # Download URL for single DB entry
    path('download/<str:api_config>/<str:record_id>/', NdrDownloadView.as_view(), name='download_record'),

    # TEST SERVER
    path('query/<str:api_request>', ApiTestView.as_view(), name='api_test')
]