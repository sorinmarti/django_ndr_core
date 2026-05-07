"""Custom CKEditor5 widgets with NDR template-tag inserter buttons."""
from django_ckeditor_5.widgets import CKEditor5Widget


class NdrCKEditor5Widget(CKEditor5Widget):
    """Drop-in replacement for CKEditor5Widget.

    Marks the textarea with ``data-ndr-ckeditor="true"`` so the
    ndr_tag_inserter.js can find it and inject the insertion button.
    """

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-ndr-ckeditor'] = 'true'
        return attrs


class NdrResultCKEditor5Widget(CKEditor5Widget):
    """CKEditor5Widget for result field expressions.

    Marks the textarea with ``data-ndr-result-editor="true"`` so the
    ndr_result_tag_inserter.js can find it and inject the field-tag button.
    """

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-ndr-result-editor'] = 'true'
        return attrs