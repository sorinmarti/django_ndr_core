"""Forms used in the NDRCore admin interface for UI elements."""
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Div
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUIElement, NdrCoreImage, NdrCoreManifestGroup


class ImageChoiceField(forms.ModelChoiceField):
    """Used to display images in a select field."""

    def label_from_instance(self, obj):
        return f'{obj.image.url}'


class UIElementForm(forms.ModelForm):
    """Form to create or edit a Card."""

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreUIElement
        fields = ['type', 'name', 'show_indicators', 'autoplay']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for x in range(0, 10):
            self.fields[f'item_{x}_ndr_banner_image'] = ImageChoiceField(
                queryset=NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.BGS),
                required=False,
                label='Background Image')
            self.fields[f'item_{x}_ndr_slide_image'] = ImageChoiceField(
                queryset=NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.ELEMENTS),
                required=False,
                label='Slide Image')
            self.fields[f'item_{x}_ndr_card_image'] = ImageChoiceField(
                queryset=NdrCoreImage.objects.filter(image_group__in=[NdrCoreImage.ImageGroup.ELEMENTS,
                                                                      NdrCoreImage.ImageGroup.FIGURES]),
                required=False,
                label='Card Image')

            self.fields[f'item_{x}_title'] = forms.CharField(required=False,
                                                             label='Title')
            self.fields[f'item_{x}_text'] = forms.CharField(widget=forms.Textarea,
                                                            required=False,
                                                            label='Text')
            self.fields[f'item_{x}_url'] = forms.URLField(required=False,
                                                          label='URL')
            self.fields[f'item_{x}_manifest_group'] = (
                forms.ModelChoiceField(label='Manifest Group',
                                       queryset=NdrCoreManifestGroup.objects.all(),
                                       required=False))

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column(Div(HTML('''
                    <br/>
                    <b>1.) Select the type of UI Element you want to create.</b>
                    &nbsp;&nbsp; 
                    <small>(Keep in mind that you need to create images first if you want to use them!)</small>
                    <hr/>
                    ''')), css_class='col-12'),
            css_class='form-row'
        )
        layout.append(form_row)

        html = HTML('<div class="text-center">'
                    '<img id="id_ui_element_preview" src="" class="img-fluid" style="width: 80%;"/>'
                    '</div>')
        form_row = Row(
            Column('type', 'name', css_class='form-group col-5'),
            Column(html, css_class='form-group col-7'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column(Div(HTML('''
                            <br/>
                            <b>2.) Configure your item(s).</b>
                            &nbsp;&nbsp; 
                            <small>(Enter your content)</small>
                            <hr/>
                            ''')), css_class='col-12'),
            css_class='form-row'
        )
        layout.append(form_row)

        tab_holder = TabHolder(css_id='my-tab-holder')
        for x in range(0, 10):
            tab = Tab(f'Item {x}', css_id=f'my-item-{x}')
            html = HTML('<div class="text-center">'
                        f'<img id="id_ui_element_{x}_preview" src="none" class="img-fluid" style="width: 80%;"/>'
                        f'</div>')
            form_row = Row(
                Column(
                    f'item_{x}_ndr_banner_image',
                    f'item_{x}_ndr_slide_image',
                    f'item_{x}_ndr_card_image',
                    f'item_{x}_title',
                    f'item_{x}_text',
                    f'item_{x}_url',
                    f'item_{x}_manifest_group',
                    css_class='col-8'
                ),
                Column(
                    html,
                    css_class='col-4'
                ),
            )
            tab.append(form_row)

            tab_holder.append(tab)

        layout.append(tab_holder)

        form_row = Row(
            Column(Div(HTML('''
                                    <br/>
                                    <b>3.) Set type-specific options.</b>
                                    &nbsp;&nbsp; 
                                    <small>(Depending on the type, different options apply)</small>
                                    <hr/>
                                    ''')), css_class='col-12'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('show_indicators', css_class='form-group col-4'),
            Column('autoplay', css_class='form-group col-4'),
            css_class='form-row'
        )
        layout.append(form_row)

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
