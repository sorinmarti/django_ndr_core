"""Forms used in the NDRCore admin interface for UI elements."""
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUIElement, NdrCoreImage


class ImageChoiceField(forms.ModelChoiceField):
    """Used to display images in a select field."""

    def label_from_instance(self, obj):
        return f'{obj.image.url}'


class ImageMultipleChoiceField(forms.ModelMultipleChoiceField):
    """Used to display images in a select field."""

    def label_from_instance(self, obj):
        return f'{obj.image.url}'


class UIElementForm(forms.ModelForm):
    """Form to create or edit a Card."""

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreUIElement
        fields = ['type', 'title',
                  'link_element', 'use_image_conf',
                  'show_title', 'show_text', 'show_image', 'show_indicators',
                  'autoplay']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for x in range(0, 10):
            self.fields[f'item_{x}_image'] = ImageChoiceField(queryset=NdrCoreImage.objects.all())

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('type', css_class='form-group col-12'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('title', css_class='form-group col-12'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('use_image_conf', css_class='form-group col-3'),
            Column('use_image_conf', css_class='form-group col-3'),
            Column('show_indicators', css_class='form-group col-3'),
            Column('show_title', css_class='form-group col-3'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('show_text', css_class='form-group col-3'),
            Column('show_image', css_class='form-group col-3'),
            Column('link_element', css_class='form-group col-3'),
            Column('autoplay', css_class='form-group col-3'),
            css_class='form-row'
        )
        layout.append(form_row)

        tab_holder = TabHolder()
        for x in range(0, 10):
            tab = Tab(f'Item {x}')
            form_row = Row(
                Column(f'item_{x}_image', css_class='form-group col-12'),
                css_class='form-row'
            )
            tab.append(form_row)
            tab_holder.append(tab)

        layout.append(tab_holder)

        return helper


class UIElementCreateForm(UIElementForm):
    """Form to create a Card. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Create New UI Element'))
        return helper


class UIElementEditForm(UIElementForm):
    """Form to create a Card. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save UI Element'))
        return helper
