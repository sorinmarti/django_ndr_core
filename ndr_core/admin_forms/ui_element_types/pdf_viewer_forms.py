"""Forms for PDF Viewer UI Element type."""
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms
from django_select2 import forms as s2forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUIElement, NdrCoreUiElementItem, NdrCoreUpload
from .base_forms import BaseUIElementForm


class PdfUploadSelect2Widget(s2forms.ModelSelect2MultipleWidget):
    """Select2 multi-select widget for NdrCoreUpload (PDF files)."""
    model = NdrCoreUpload
    search_fields = ['title__icontains', 'file__icontains']


class PdfViewerForm(BaseUIElementForm):
    """Form for PDF Viewer UI Element — embeds one or more uploaded PDFs."""

    pdf_files = forms.ModelMultipleChoiceField(
        queryset=NdrCoreUpload.objects.all().order_by('-id'),
        required=True,
        label='PDF File(s)',
        help_text=(
            'Select one or more uploaded PDF files. '
            'Multiple selections show a dropdown selector in the viewer.'
        ),
        widget=PdfUploadSelect2Widget(attrs={'data-minimum-input-length': 0}),
    )
    title = forms.CharField(
        max_length=200,
        required=False,
        label='Title',
        help_text='Optional heading shown above the viewer.'
    )
    text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Description',
        help_text='Optional description shown above the viewer.'
    )
    height = forms.IntegerField(
        required=False,
        initial=800,
        min_value=200,
        label='Viewer Height (px)',
        help_text='Height of the embedded PDF viewer in pixels. Default: 800.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ui_element_type='pdf_viewer', **kwargs)

    def save(self, commit=True):
        """Save the PDF Viewer UI Element — one NdrCoreUiElementItem per selected PDF."""
        instance = super().save(commit=commit)

        if commit:
            instance.ndrcoreuielementitem_set.all().delete()
            pdf_files = self.cleaned_data.get('pdf_files', [])
            height = str(self.cleaned_data.get('height') or 800)
            title = self.cleaned_data.get('title', '')
            text = self.cleaned_data.get('text', '')

            for idx, pdf_file in enumerate(pdf_files):
                NdrCoreUiElementItem.objects.create(
                    belongs_to=instance,
                    order_idx=idx,
                    upload_file=pdf_file,
                    title=title if idx == 0 else '',
                    text=text if idx == 0 else '',
                    object_id=height,   # stored on every item for easy retrieval
                )

        return instance

    @property
    def helper(self):
        helper = self.get_base_helper()
        layout = helper.layout

        self.add_info_section(
            layout,
            'PDF Viewer UI Element',
            'Embed one or more uploaded PDFs using the browser\'s native PDF renderer. '
            'Selecting multiple files adds a dropdown to switch between them. '
            'Upload PDF files in the Uploads section first.'
        )

        self.add_field_row(layout, 'name', 'label', col_class='col-md-6')

        layout.append(Row(
            Column(HTML('<h5 class="mt-3 mb-3">PDF Configuration</h5>'), css_class='col-12'),
            css_class='row g-2'
        ))

        self.add_field_row(layout, 'pdf_files', col_class='col-md-8')
        self.add_field_row(layout, 'height', col_class='col-md-4')
        self.add_field_row(layout, 'title', col_class='col-md-6')
        self.add_field_row(layout, 'text', col_class='col-md-12')

        return helper


class PdfViewerCreateForm(PdfViewerForm):
    """Form to create a new PDF Viewer UI Element."""

    @property
    def helper(self):
        helper = super().helper
        helper.layout.append(get_form_buttons('Create PDF Viewer'))
        return helper


class PdfViewerEditForm(PdfViewerForm):
    """Form to edit an existing PDF Viewer UI Element."""

    def __init__(self, *args, **kwargs):
        self._original_name = kwargs['instance'].name if 'instance' in kwargs else None
        super().__init__(*args, **kwargs)

        self.fields['name'].help_text = (
            'Unique slug/identifier. Can be changed — renaming will preserve all settings.'
        )

        if self.instance and self.instance.pk:
            items = self.instance.items()
            if items:
                self.fields['pdf_files'].initial = [
                    item.upload_file.pk for item in items if item.upload_file
                ]
                self.fields['title'].initial = items[0].title
                self.fields['text'].initial = items[0].text
                try:
                    self.fields['height'].initial = int(items[0].object_id) if items[0].object_id else 800
                except (ValueError, TypeError):
                    self.fields['height'].initial = 800

    def save(self, commit=True):
        name_changed = self._original_name and self._original_name != self.cleaned_data.get('name')

        if name_changed and commit:
            old_instance = NdrCoreUIElement.objects.get(name=self._original_name)
            new_instance = super().save(commit=True)
            old_instance.delete()
            return new_instance
        else:
            return super().save(commit=commit)

    @property
    def helper(self):
        helper = super().helper
        helper.layout.append(get_form_buttons('Save PDF Viewer'))
        return helper
