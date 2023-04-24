from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from ndr_core.admin_views.uploads_views import ConfigureUploads, UploadCreateView, UploadEditView, UploadDeleteView
from ndr_core.admin_views.result_views import ConfigureResultsView, ResultsConfigurationDetailView
from ndr_core.admin_views.export_views import export_color_palette, export_settings, export_messages
from ndr_core.admin_views.admin_views import NdrCoreDashboard, HelpView, StatisticsView, \
    set_statistics_option
from ndr_core.admin_views.page_views import ManagePages, PageCreateView, PageEditView, PageDeleteView, PageDetailView, \
    move_page_up, ManagePageFooter
from ndr_core.admin_views.api_views import ConfigureApi, ApiConfigurationCreateView, ApiConfigurationEditView, \
    ApiConfigurationDeleteView, ApiConfigurationDetailView
from ndr_core.admin_views.search_views import ConfigureSearch, SearchConfigurationCreateView, \
    SearchConfigurationEditView, SearchConfigurationDeleteView, SearchFieldConfigurationCreateView, \
    SearchFieldConfigurationEditView, SearchFieldConfigurationDeleteView, preview_image, create_search_fields
from ndr_core.admin_views.color_views import ConfigureColorPalettes, ColorPaletteCreateView, ColorPaletteEditView, \
    ColorPaletteDeleteView, ColorPaletteImportView, ColorPaletteDetailView, choose_color_palette
from ndr_core.admin_views.corrections_views import ConfigureCorrections, set_correction_option
from ndr_core.admin_views.images_views import ConfigureImages, ImagesGroupView, LogoUploadView, ImagesCreateView, \
    ImagesEditView, ImagesDeleteView, move_image_up
from ndr_core.admin_views.settings_views import ConfigureSettingsView, SettingCreateView, SettingsDetailView, \
    SettingEditView, SettingDeleteView, SettingsImportView
from ndr_core.admin_views.ui_style_views import ConfigureUI, choose_ui_style, UIStyleDetailView
from ndr_core.admin_views.ui_element_views import ConfigureUIElements, UIElementDetailView, UIElementCreateView, \
    UIElementEditView, UIElementDeleteView
from ndr_core.admin_views.messages_views import ConfigureMessages, MessagesView, MessagesDeleteView, \
    delete_all_messages, archive_message, ArchivedMessages
from ndr_core.admin_views.sample_data_views import SampleDataView, SampleDataDetailView, SampleDataUploadView, \
    SampleDataDeleteView

from ndr_core.admin_forms.admin_forms import NdrCoreLoginForm, NdrCoreChangePasswordForm
from ndr_core.views import ApiTestView, NdrDownloadView, NdrMarkForCorrectionView, NdrListDownloadView, NdrCSVListDownloadView

app_name = 'ndr_core'
urlpatterns = [
    path('', NdrCoreDashboard.as_view(), name='dashboard'),

    # PAGES
    path('configure/pages/', ManagePages.as_view(), name='configure_pages'),
    path('configure/pages/footer/', ManagePageFooter.as_view(), name='page_footer'),
    path('configure/pages/view/<int:pk>/', PageDetailView.as_view(), name='view_page'),
    path('configure/pages/create/new/', PageCreateView.as_view(), name='create_page'),
    path('configure/pages/edit/<int:pk>/', PageEditView.as_view(), name='edit_page'),
    path('configure/pages/delete/<int:pk>/', PageDeleteView.as_view(), name='delete_page'),
    path('configure/pages/move/up/<int:pk>/', move_page_up, name='move_page_up'),

    # SETTINGS
    path('configure/settings/', ConfigureSettingsView.as_view(), name='configure_settings'),
    path('configure/settings/<str:group>/', SettingsDetailView.as_view(), name='view_settings'),
    path('configure/settings/create/new/', SettingCreateView.as_view(), name='create_setting'),
    path('configure/colors/import/', SettingsImportView.as_view(), name='import_settings'),
    path('configure/colors/export/', export_settings, name='export_settings'),
    path('configure/settings/edit/<str:pk>/', SettingEditView.as_view(), name='edit_setting'),
    path('configure/settings/delete/<str:pk>/', SettingDeleteView.as_view(), name='delete_setting'),

    # UI STYLE
    path('configure/ui_settings/', ConfigureUI.as_view(), name='ui_settings'),
    path('configure/ui_settings/view/<str:pk>/', UIStyleDetailView.as_view(), name='view_ui_style'),
    path('configure/ui_settings/choose/<str:pk>/', choose_ui_style, name='choose_ui_settings'),

    # IMAGES
    path('configure/images/', ConfigureImages.as_view(), name='configure_images'),
    path('configure/images/view/<str:group>/', ImagesGroupView.as_view(), name='view_images'),
    path('configure/images/change/logo/', LogoUploadView.as_view(), name='import_logo'),
    path('configure/images/create/new/', ImagesCreateView.as_view(), name='create_image'),
    path('configure/images/edit/<int:pk>/', ImagesEditView.as_view(), name='edit_image'),
    path('configure/images/delete/<int:pk>/', ImagesDeleteView.as_view(), name='delete_image'),
    path('configure/images/move/up/<int:pk>/', move_image_up, name='move_image_up'),

    # UPLOADS
    path('configure/uploads/', ConfigureUploads.as_view(), name='configure_uploads'),
    path('configure/uploads/create/new/', UploadCreateView.as_view(), name='create_upload'),
    path('configure/uploads/edit/<int:pk>/', UploadEditView.as_view(), name='edit_upload'),
    path('configure/uploads/delete/<int:pk>/', UploadDeleteView.as_view(), name='delete_upload'),

    # USER MESSAGES
    path('configure/messages/', ConfigureMessages.as_view(), name='configure_messages'),
    path('configure/messages/archived/', ArchivedMessages.as_view(), name='archived_messages'),
    path('configure/messages/view/<int:pk>/', MessagesView.as_view(), name='view_message'),
    path('configure/messages/delete/<int:pk>/', MessagesDeleteView.as_view(), name='delete_message'),
    path('configure/messages/archive/<int:pk>/', archive_message, name='archive_message'),
    path('configure/messages/export/', export_messages, name='export_messages'),
    path('configure/messages/delete/all/', delete_all_messages, name='delete_all_messages'),

    # CORRECTIONS
    path('configure/corrections/', ConfigureCorrections.as_view(), name='configure_corrections'),
    path('configure/corrections/enable/<str:option>/', set_correction_option, name='set_correction_option'),

    # COLOR PALETTES
    path('configure/colors/', ConfigureColorPalettes.as_view(), name='configure_colors'),
    path('configure/colors/view/<str:pk>/', ColorPaletteDetailView.as_view(), name='view_palette'),
    path('configure/colors/create/new/', ColorPaletteCreateView.as_view(), name='create_palette'),
    path('configure/colors/import/new/', ColorPaletteImportView.as_view(), name='import_palette'),
    path('configure/colors/edit/<str:pk>/', ColorPaletteEditView.as_view(), name='edit_palette'),
    path('configure/colors/delete/<str:pk>/', ColorPaletteDeleteView.as_view(), name='delete_palette'),
    path('configure/colors/choose/<str:pk>/', choose_color_palette, name='choose_palette'),
    path('configure/colors/export/<str:pk>/', export_color_palette, name='export_palette'),

    # UI ELEMENTS
    path('configure/ui_elements/', ConfigureUIElements.as_view(), name='configure_ui_elements'),
    path('configure/ui_elements/view/<str:pk>/', UIElementDetailView.as_view(), name='view_ui_element'),
    path('configure/ui_elements/create/new/<str:type>/', UIElementCreateView.as_view(), name='create_ui_element'),
    path('configure/ui_elements/edit/<str:pk>/', UIElementEditView.as_view(), name='edit_ui_element'),
    path('configure/ui_elements/delete/<str:pk>/', UIElementDeleteView.as_view(), name='delete_ui_element'),

    # API
    path('configure/api/', ConfigureApi.as_view(), name='configure_api'),
    path('configure/api/view/<str:pk>/', ApiConfigurationDetailView.as_view(), name='view_api'),
    path('configure/api/create/new/', ApiConfigurationCreateView.as_view(), name='create_api'),
    path('configure/api/edit/<str:pk>/', ApiConfigurationEditView.as_view(), name='edit_api'),
    path('configure/api/delete/<str:pk>/', ApiConfigurationDeleteView.as_view(), name='delete_api'),

    # SEARCH CONFIG
    path('configure/search/', ConfigureSearch.as_view(), name='configure_search'),
    path('configure/search/create/new/', SearchConfigurationCreateView.as_view(), name='create_search'),
    path('configure/search/edit/<str:pk>/', SearchConfigurationEditView.as_view(), name='edit_search'),
    path('configure/search/delete/<str:pk>/', SearchConfigurationDeleteView.as_view(), name='delete_search'),
    path('configure/search/image/preview/<str:img_config>/', preview_image, name='preview_image'),

    # SEARCH FIELDS
    path('configure/search/fields/create/new/', SearchFieldConfigurationCreateView.as_view(), name='create_search_field'),
    path('configure/search/fields/edit/<str:pk>/', SearchFieldConfigurationEditView.as_view(), name='edit_search_field'),
    path('configure/search/fields/delete/<str:pk>/', SearchFieldConfigurationDeleteView.as_view(), name='delete_search_field'),
    path('configure/search/fields/schema/<int:schema_pk>/', create_search_fields, name='create_fields_from_schema'),

    # CONFIGURE DATA
    path('configure/data/', SampleDataView.as_view(), name='configure_sample_data'),
    path('configure/data/view/<str:pk>/<str:filename>/', SampleDataDetailView.as_view(), name='view_sample_data'),
    path('configure/data/delete/<str:pk>/<str:filename>/', SampleDataDeleteView.as_view(), name='delete_sample_data_file'),
    path('configure/data/upload/', SampleDataUploadView.as_view(), name='upload_sample_data'),

    # RESULTS
    path('configure/results/', ConfigureResultsView.as_view(), name='configure_results'),
    path('configure/results/<str:search_config>/', ResultsConfigurationDetailView.as_view(), name='configure_result'),

    # SEARCH STATS
    path('search/statistics/', StatisticsView.as_view(), name='search_statistics'),
    path('search/statistics/enable/<str:option>/', set_statistics_option, name='set_statistics_option'),

    # Login / Logout
    path('login/', auth_views.LoginView.as_view(template_name='ndr_core/admin_views/login.html',
                                                form_class=NdrCoreLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='ndr_core/admin_views/logout.html'), name='logout'),
    path('change_password/',
         auth_views.PasswordChangeView.as_view(template_name='ndr_core/admin_views/change_password.html',
                                               form_class=NdrCoreChangePasswordForm,
                                               success_url=reverse_lazy('ndr_core:password_change_done')),
         name='change_password'),
    path('password_changed/', TemplateView.as_view(template_name='ndr_core/admin_views/password_changed.html'), name='password_change_done'),

    # Help
    path('help/', HelpView.as_view(), name='help'),
    path('help/<str:chapter>/', HelpView.as_view(), name='help_chapter'),

    # Download URL for single DB entry
    path('download/<str:search_config>/<str:record_id>/', NdrDownloadView.as_view(), name='download_record'),
    path('bulk-download/json/<str:search_config>/', NdrListDownloadView.as_view(), name='download_list'),
    path('bulk-download/csv/<str:search_config>/', NdrCSVListDownloadView.as_view(), name='download_csv'),

    # Mark an entry for correction
    path('mark/to/correct/<str:api_config>/<str:record_id>/', NdrMarkForCorrectionView.as_view(), name='mark_record'),

    # TEST SERVER
    path('query/<str:api_request>', ApiTestView.as_view(), name='api_test')
]