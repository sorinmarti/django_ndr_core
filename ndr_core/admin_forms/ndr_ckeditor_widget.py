"""Custom CKEditor5 widget with NDR template-tag inserter button."""
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