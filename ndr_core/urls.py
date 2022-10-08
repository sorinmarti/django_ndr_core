from django.urls import path
from django.contrib.auth import views as auth_views

from ndr_core.admin_forms import NdrCoreLoginForm
from ndr_core.admin_views import create_search_fields, dummy, PageEditView, PageDeleteView, move_page_up, \
    ConfigureSettings, ApiConfigurationCreateView, ApiConfigurationEditView
from ndr_core.admin_views import NdrCoreDashboard, ManagePages, ConfigureApi, ConfigureSearch, ConfigureSearchFields, \
    PageCreateView

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

    # API
    path('configure/api/', ConfigureApi.as_view(), name='configure_api'),
    path('configure/api/create/new/', ApiConfigurationCreateView.as_view(), name='create_api'),
    path('configure/api/edit/<int:pk>/', ApiConfigurationEditView.as_view(), name='edit_api'),

    # SEARCH CONFIG
    path('configure/search/', ConfigureSearch.as_view(), name='configure_search'),
    path('configure/search/fields/', ConfigureSearchFields.as_view(), name='configure_search_fields'),
    path('configure/search/fields/schema/<int:schema_pk>/', create_search_fields, name='create_fields_from_schema'),
    path('configure/search/fields/create/new/', dummy, name='create_search_field'),

    # Login / Logout
    path('login/', auth_views.LoginView.as_view(template_name='ndr_core/admin_views/login.html',
                                                form_class=NdrCoreLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='ndr_core/admin_views/logout.html'), name='logout')
]