"""Forms used in the NDRCore admin interface for UI elements."""
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML
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


class UIElementBaseForm(forms.ModelForm):
    """TODO Create base form for UI elements and remove redundant code."""

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreUIElement
        fields = ['show_text', ]

    def __init__(self, *args, **kwargs):
        super(UIElementBaseForm, self).__init__(*args, **kwargs)
        self.fields['text'] = forms.CharField(widget=forms.Textarea, required=False)

    def initialize_field(self, field_name):
        if field_name == "card_item_image":
            self.fields[field_name] = ImageChoiceField(
                queryset=NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.BGS), empty_label=None)
            self.fields[field_name].widget.option_template_name = "ndr_core/test.html"


class UIElementCardForm(forms.ModelForm):

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreUIElement
        fields = ['show_title', 'show_text', 'show_image', 'link_element', 'use_image_conf']

    def __init__(self, *args, **kwargs):
        super(UIElementCardForm, self).__init__(*args, **kwargs)

        self.fields['card_item_image'] = ImageChoiceField(queryset=NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.BGS), empty_label=None)
        self.fields['card_item_image'].widget.option_template_name = "ndr_core/test.html"
        self.fields['card_item_title'] = forms.CharField(required=False)
        self.fields['card_item_text'] = forms.CharField(widget=forms.Textarea, required=False)
        self.fields['card_item_url'] = forms.URLField(required=False)

        self.fields['show_image'].label = 'Does this card feature an image?'
        self.fields['show_image'].help_text = 'Note: Images must be uploaded first, before they can be used in UI elements.'

        self.fields['use_image_conf'].label = 'Should this card display the image\'s title, text and URL?'

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('show_image', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_image', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('use_image_conf', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_title', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_text', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_url', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('show_title', css_class='form-group col-md-4 mb-0'),
            Column('show_text', css_class='form-group col-md-4 mb-0'),
            Column('link_element', css_class='form-group col-md-4 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        return helper


class UIElementSlideshowForm(forms.ModelForm):

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreUIElement
        fields = ['title', 'show_title', 'show_text', 'link_element', 'autoplay', 'show_indicators']

    def __init__(self, *args, **kwargs):
        super(UIElementSlideshowForm, self).__init__(*args, **kwargs)
        self.fields['slideshow_images'] = ImageMultipleChoiceField(queryset=NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.BGS))
        self.fields['slideshow_images'].widget.option_template_name = "ndr_core/test.html"

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('title', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('slideshow_images', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('show_title', css_class='form-group col-md-4 mb-0'),
            Column('show_text', css_class='form-group col-md-4 mb-0'),
            Column('link_element', css_class='form-group col-md-4 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('show_indicators', css_class='form-group col-md-4 mb-0'),
            Column('autoplay', css_class='form-group col-md-4 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        return helper


class UIElementCarouselForm(forms.ModelForm):

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreUIElement
        fields = ['title', 'show_title', 'show_text', 'link_element', 'autoplay', 'show_indicators']

    def __init__(self, *args, **kwargs):
        super(UIElementCarouselForm, self).__init__(*args, **kwargs)

        for x in range(6):
            self.fields[f'card_item_active_{x}'] = forms.BooleanField()
            self.fields[f'card_item_has_image_{x}'] = forms.BooleanField()
            self.fields[f'card_item_use_image_{x}'] = forms.BooleanField()
            self.fields[f'card_item_image_{x}'] = ImageChoiceField(
                queryset=NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.BGS), empty_label=None)
            self.fields[f'card_item_image_{x}'].widget.option_template_name = "ndr_core/test.html"

            self.fields[f'card_item_title_{x}'] = forms.CharField()
            self.fields[f'card_item_url_{x}'] = forms.URLField()
            self.fields[f'card_item_text_{x}'] = forms.CharField(widget=forms.Textarea)

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('title', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        tab_holder = TabHolder()
        for x in range(6):
            tab = Tab(f'Carousel Item {x+1}')

            form_row = Row(
                Column(f'card_item_active_{x}', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            )
            tab.append(form_row)

            form_row = Row(
                Column(f'card_item_has_image_{x}', css_class='form-group col-md-6 mb-0'),
                Column(f'card_item_use_image_{x}', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            )
            tab.append(form_row)

            form_row = Row(
                Column(f'card_item_image_{x}', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            )
            tab.append(form_row)

            form_row = Row(
                Column(f'card_item_title_{x}', css_class='form-group col-md-6 mb-0'),
                Column(f'card_item_url_{x}', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            )
            tab.append(form_row)

            form_row = Row(
                Column(f'card_item_text_{x}', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            )
            tab.append(form_row)

            tab_holder.append(tab)
        layout.append(tab_holder)

        form_row = Row(
            Column('show_title', css_class='form-group col-md-4 mb-0'),
            Column('show_text', css_class='form-group col-md-4 mb-0'),
            Column('link_element', css_class='form-group col-md-4 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('show_indicators', css_class='form-group col-md-4 mb-0'),
            Column('autoplay', css_class='form-group col-md-4 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        return helper


class UIElementJumbotronForm(forms.ModelForm):

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreUIElement
        fields = ['show_title', 'show_text', 'show_image', 'link_element', 'use_image_conf']

    def __init__(self, *args, **kwargs):
        super(UIElementJumbotronForm, self).__init__(*args, **kwargs)
        self.fields[f'card_item_image'] = ImageChoiceField(queryset=NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.BGS), empty_label=None)
        self.fields['card_item_image'].widget.option_template_name = "ndr_core/test.html"
        self.fields[f'card_item_title'] = forms.CharField()
        self.fields[f'card_item_text'] = forms.CharField(widget=forms.Textarea)
        self.fields[f'card_item_url'] = forms.URLField()

        self.fields['show_image'].label = 'Does this card feature an image?'
        self.fields['show_image'].help_text = 'Note: Images must be uploaded first, before they can be used in UI elements.'

        self.fields['use_image_conf'].label = 'Should this card display the image\'s title, text and URL?'

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('show_image', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_image', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('use_image_conf', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_title', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_text', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_url', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('show_title', css_class='form-group col-md-4 mb-0'),
            Column('show_text', css_class='form-group col-md-4 mb-0'),
            Column('link_element', css_class='form-group col-md-4 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        return helper


class UIElementIframeForm(forms.ModelForm):

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreUIElement
        fields = ['show_title', 'show_text', 'show_image', 'link_element', 'use_image_conf']

    def __init__(self, *args, **kwargs):
        super(UIElementIframeForm, self).__init__(*args, **kwargs)
        self.fields[f'card_item_image'] = ImageChoiceField(queryset=NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.BGS), empty_label=None)
        self.fields['card_item_image'].widget.option_template_name = "ndr_core/test.html"
        self.fields[f'card_item_title'] = forms.CharField()
        self.fields[f'card_item_text'] = forms.CharField(widget=forms.Textarea)
        self.fields[f'card_item_url'] = forms.URLField()

        self.fields['show_image'].label = 'Does this card feature an image?'
        self.fields['show_image'].help_text = 'Note: Images must be uploaded first, before they can be used in UI elements.'

        self.fields['use_image_conf'].label = 'Should this card display the image\'s title, text and URL?'

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('show_image', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_image', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('use_image_conf', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_title', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_text', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_url', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('show_title', css_class='form-group col-md-4 mb-0'),
            Column('show_text', css_class='form-group col-md-4 mb-0'),
            Column('link_element', css_class='form-group col-md-4 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        return helper


class UIElementBannerForm(forms.ModelForm):

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreUIElement
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super(UIElementBannerForm, self).__init__(*args, **kwargs)
        self.fields['card_item_image'] = ImageChoiceField(queryset=NdrCoreImage.objects.filter(image_group=NdrCoreImage.ImageGroup.BGS), empty_label=None)
        self.fields['card_item_image'].widget.option_template_name = "ndr_core/test.html"

    @property
    def helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('title', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('card_item_image', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        return helper


class UIElementCardCreateForm(UIElementCardForm):
    """Form to create a Card. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementCardCreateForm, self).helper
        helper.layout.append(get_form_buttons('Create New Card'))
        return helper


class UIElementCardEditForm(UIElementCardForm):
    """Form to create a Card. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementCardEditForm, self).helper
        helper.layout.append(get_form_buttons('Save Card'))
        return helper


class UIElementSlideshowCreateForm(UIElementSlideshowForm):
    """Form to create a Card. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementSlideshowCreateForm, self).helper
        helper.layout.append(get_form_buttons('Create New Slideshow'))
        return helper


class UIElementSlideshowEditForm(UIElementSlideshowForm):
    """Form to create a Card. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementSlideshowEditForm, self).helper
        helper.layout.append(get_form_buttons('Save Slideshow'))
        return helper


class UIElementCarouselCreateForm(UIElementCarouselForm):
    """Form to create a Carousel. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementCarouselCreateForm, self).helper
        helper.layout.append(get_form_buttons('Create New Carousel'))
        return helper


class UIElementCarouselEditForm(UIElementCarouselForm):
    """Form to create a Carousel. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementCarouselEditForm, self).helper
        helper.layout.append(get_form_buttons('Save Carousel'))
        return helper


class UIElementJumbotronCreateForm(UIElementJumbotronForm):
    """Form to create a Jumbotron. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementJumbotronCreateForm, self).helper
        helper.layout.append(get_form_buttons('Create New Jumbotron'))
        return helper


class UIElementJumbotronEditForm(UIElementJumbotronForm):
    """Form to create a Jumbotron. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementJumbotronEditForm, self).helper
        helper.layout.append(get_form_buttons('Save Jumbotron'))
        return helper


class UIElementIframeCreateForm(UIElementIframeForm):
    """Form to create an Iframe. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementIframeCreateForm, self).helper
        helper.layout.append(get_form_buttons('Create New Iframe'))
        return helper


class UIElementIframeEditForm(UIElementIframeForm):
    """Form to create an Iframe. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementIframeEditForm, self).helper
        helper.layout.append(get_form_buttons('Save Iframe'))
        return helper


class UIElementBannerCreateForm(UIElementBannerForm):
    """Form to create a Banner. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementBannerCreateForm, self).helper
        helper.layout.append(get_form_buttons('Create New Banner'))
        return helper


class UIElementBannerEditForm(UIElementBannerForm):
    """Form to create a Banner. Extends the base form class and adds a 'create' button."""

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super(UIElementBannerEditForm, self).helper
        helper.layout.append(get_form_buttons('Save Banner'))
        return helper