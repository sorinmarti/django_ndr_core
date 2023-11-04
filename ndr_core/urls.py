from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from ndr_core.admin_views.result_views import ResultFieldCreateView, ResultFieldEditView, preview_result_card_image, \
    ResultFieldDeleteView, SearchConfigurationResultEditView
from ndr_core.admin_views.search_field_views import SearchFieldCreateView, SearchFieldEditView, \
    preview_search_form_image, SearchFieldDeleteView
from ndr_core.admin_views.translation_views import (
    ConfigureTranslations,
    SelectPageTranslationView,
    SelectFieldTranslationView,
    TranslatePageValuesView,
    TranslateFieldValuesView,
    SelectSettingsTranslationView,
    TranslateSettingsValuesView,
    TranslateFormValuesView,
    SelectFormTranslationView,
)
from ndr_core.admin_views.uploads_views import (
    ConfigureUploads,
    UploadCreateView,
    UploadEditView,
    UploadDeleteView,
    ManifestUploadCreateView,
    ManifestUploadEditView,
    ManifestUploadDeleteView,
    ManifestGroupCreateView,
)
from ndr_core.admin_views.export_views import export_color_palette, export_settings, export_messages
from ndr_core.admin_views.admin_views import NdrCoreDashboard, HelpView, StatisticsView, \
    set_statistics_option
from ndr_core.admin_views.page_views import (
    ManagePages,
    PageCreateView,
    PageEditView,
    PageDeleteView,
    PageDetailView,
    move_page_up,
    ManagePageFooter,
)

from ndr_core.admin_views.search_views import ConfigureSearch, SearchConfigurationCreateView, \
    SearchConfigurationEditView, SearchConfigurationDeleteView, SearchConfigurationFormEditView, \
    SearchConfigurationCopyView
from ndr_core.admin_views.color_views import ConfigureColorPalettes, ColorPaletteCreateView, ColorPaletteEditView, \
    ColorPaletteDeleteView, ColorPaletteImportView, ColorPaletteDetailView, choose_color_palette
from ndr_core.admin_views.corrections_views import ConfigureCorrections, set_correction_option
from ndr_core.admin_views.images_views import ConfigureImages, ImagesGroupView, ImagesCreateView, \
    ImagesEditView, ImagesDeleteView, move_image_up
from ndr_core.admin_views.settings_views import (
    ConfigureSettingsView,
    SettingCreateView,
    SettingsDetailView,
    SettingEditView,
    SettingDeleteView,
    SettingsImportView,
    SetPageReadOnlyView,
    SetPageEditableView,
    SetPageUnderConstructionView,
    SetPageLiveView,
)
from ndr_core.admin_views.ui_style_views import ConfigureUI, choose_ui_style, UIStyleDetailView
from ndr_core.admin_views.ui_element_views import ConfigureUIElements, UIElementDetailView, UIElementCreateView, \
    UIElementEditView, UIElementDeleteView
from ndr_core.admin_views.messages_views import ConfigureMessages, MessagesView, MessagesDeleteView, \
    delete_all_messages, archive_message, ArchivedMessages

from ndr_core.admin_forms.admin_forms import NdrCoreLoginForm, NdrCoreChangePasswordForm
from ndr_core.views import NdrDownloadView, NdrMarkForCorrectionView, NdrListDownloadView, \
    NdrCSVListDownloadView, set_language_view

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
    path('configure/settings/set/readonly/', SetPageReadOnlyView.as_view(), name='set_page_read_only'),
    path('configure/settings/set/editable/', SetPageEditableView.as_view(), name='set_page_editable'),
    path('configure/settings/set/under_construction/', SetPageUnderConstructionView.as_view(), name='set_page_under_construction'),
    path('configure/settings/set/live/', SetPageLiveView.as_view(), name='set_page_live'),


    # UI STYLE
    path('configure/ui_settings/', ConfigureUI.as_view(), name='ui_settings'),
    path('configure/ui_settings/view/<str:pk>/', UIStyleDetailView.as_view(), name='view_ui_style'),
    path('configure/ui_settings/choose/<str:pk>/', choose_ui_style, name='choose_ui_settings'),

    # IMAGES
    path('configure/images/', ConfigureImages.as_view(), name='configure_images'),
    path('configure/images/view/<str:group>/', ImagesGroupView.as_view(), name='view_images'),
    path('configure/images/create/new/', ImagesCreateView.as_view(), name='create_image'),
    path('configure/images/edit/<int:pk>/', ImagesEditView.as_view(), name='edit_image'),
    path('configure/images/delete/<int:pk>/', ImagesDeleteView.as_view(), name='delete_image'),
    path('configure/images/move/up/<int:pk>/', move_image_up, name='move_image_up'),

    # UPLOADS
    path('configure/uploads/', ConfigureUploads.as_view(), name='configure_uploads'),
    path('configure/uploads/create/new/', UploadCreateView.as_view(), name='create_upload'),
    path('configure/uploads/edit/<int:pk>/', UploadEditView.as_view(), name='edit_upload'),
    path('configure/uploads/delete/<int:pk>/', UploadDeleteView.as_view(), name='delete_upload'),
    path('configure/manifest/uploads/create/new/', ManifestUploadCreateView.as_view(), name='create_manifest_upload'),
    path('configure/manifest/uploads/edit/<int:pk>/', ManifestUploadEditView.as_view(), name='edit_manifest_upload'),
    path('configure/manifest/uploads/delete/<int:pk>/', ManifestUploadDeleteView.as_view(), name='delete_manifest_upload'),
    path('configure/manifest/groups/create/', ManifestGroupCreateView.as_view(), name='create_manifest_group'),

    # TRANSLATIONS
    path('configure/translations/', ConfigureTranslations.as_view(), name='configure_translations'),
    path('configure/translations/edit/pages/', SelectPageTranslationView.as_view(), name='select_page_translations'),
    path('configure/translations/edit/pages/<str:lang>/', TranslatePageValuesView.as_view(), name='edit_page_translations'),
    path('configure/translations/edit/fields/', SelectFieldTranslationView.as_view(), name='select_field_translations'),
    path('configure/translations/edit/fields/<str:lang>/', TranslateFieldValuesView.as_view(), name='edit_field_translations'),
    path('configure/translations/edit/settings/', SelectSettingsTranslationView.as_view(), name='select_settings_translations'),
    path('configure/translations/edit/settings/<str:lang>/', TranslateSettingsValuesView.as_view(), name='edit_settings_translations'),
    path('configure/translations/edit/form/', SelectFormTranslationView.as_view(), name='select_form_translations'),
    path('configure/translations/edit/form/<str:lang>/', TranslateFormValuesView.as_view(), name='edit_form_translations'),

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

    # SEARCH CONFIGURATIONS
    path('configure/search/', ConfigureSearch.as_view(), name='configure_search'),

    path('configure/search/create/new/config/', SearchConfigurationCreateView.as_view(), name='create_search_config'),
    path('configure/search/create/new/search_field/', SearchFieldCreateView.as_view(), name='create_search_field'),
    path('configure/search/create/new/result_field/', ResultFieldCreateView.as_view(), name='create_result_field'),

    path('configure/search/edit/config/<str:pk>/', SearchConfigurationEditView.as_view(), name='edit_search_config'),
    path('configure/search/edit/form/<str:pk>/', SearchConfigurationFormEditView.as_view(), name='edit_search_form'),
    path('configure/search/edit/card/<str:pk>/', SearchConfigurationResultEditView.as_view(), name='edit_result_card'),
    path('configure/search/edit/search_field/<str:pk>/', SearchFieldEditView.as_view(), name='edit_search_field'),
    path('configure/search/edit/result_field/<str:pk>/', ResultFieldEditView.as_view(), name='edit_result_field'),

    path('configure/search/delete/config/<str:pk>/', SearchConfigurationDeleteView.as_view(), name='delete_search_config'),
    path('configure/search/delete/search_field/<str:pk>/', SearchFieldDeleteView.as_view(), name='delete_search_field'),
    path('configure/search/delete/result_field/<str:pk>/', ResultFieldDeleteView.as_view(), name='delete_result_field'),

    path('configure/search/copy/config/<str:pk>/', SearchConfigurationCopyView.as_view(), name='copy_search_config'),
    path('configure/search/form/preview/<str:img_config>/', preview_search_form_image, name='preview_search_form_image'),
    path('configure/search/result/preview/<str:img_config>/', preview_result_card_image, name='preview_result_card_image'),

    # SEARCH STATS
    path('search/statistics/', StatisticsView.as_view(), name='search_statistics'),
    path('search/statistics/enable/<str:option>/', set_statistics_option, name='set_statistics_option'),

    # Login / Logout
    path('login/', auth_views.LoginView.as_view(template_name='ndr_core/admin_views/user_management/login.html',
                                                form_class=NdrCoreLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='ndr_core/admin_views/user_management/logout.html'), name='logout'),
    path('change_password/',
         auth_views.PasswordChangeView.as_view(template_name='ndr_core/admin_views/user_management/change_password.html',
                                               form_class=NdrCoreChangePasswordForm,
                                               success_url=reverse_lazy('ndr_core:password_change_done')),
         name='change_password'),
    path('password_changed/', TemplateView.as_view(template_name='ndr_core/admin_views/user_management/password_changed.html'), name='password_change_done'),

    # Help
    path('help/', HelpView.as_view(), name='help'),
    path('help/<str:chapter>/', HelpView.as_view(), name='help_chapter'),

    # Download URL for single DB entry
    path('download/<str:search_config>/<str:record_id>/', NdrDownloadView.as_view(), name='download_record'),
    path('bulk-download/json/<str:search_config>/', NdrListDownloadView.as_view(), name='download_list'),
    path('bulk-download/csv/<str:search_config>/', NdrCSVListDownloadView.as_view(), name='download_csv'),

    # Mark an entry for correction
    path('mark/to/correct/<str:search_config>/<str:record_id>/', NdrMarkForCorrectionView.as_view(), name='mark_record'),

    # Language
    path('language/<str:new_language>/', set_language_view, name='set_language'),

    path('test/', TemplateView.as_view(template_name='ndr_core/test.html'), name='test'),
    path('niy/', TemplateView.as_view(template_name='ndr_core/test.html'), name='not_implemented')
]