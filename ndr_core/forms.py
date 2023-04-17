import csv
import os

from captcha.fields import ReCaptchaField
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, Div, BaseInput, HTML
from django import forms
from django.db.models import Max
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ndr_core.models import NdrCoreValue, NdrCorePage, NdrCoreUserMessage, NdrCoreSearchConfiguration
from django_select2 import forms as s2forms
from bootstrap_daterangepicker import widgets, fields

from ndr_core.widgets import BootstrapSwitchWidget


class _NdrCoreForm(forms.Form):
    """Base form class for all (non-admin) NDR Core forms.  """

    ndr_page = None

    def __init__(self, *args, **kwargs):
        """Init the form class. Save the ndr page if it is provided."""
        if 'ndr_page' in kwargs:
            self.ndr_page = kwargs.pop('ndr_page')
        if 'search_config' in kwargs:
            self.search_config_name = kwargs.pop('search_config')
        if 'instance' in kwargs:
            kwargs.pop('instance')

        super(forms.Form, self).__init__(*args, **kwargs)

    def querydict_to_dict(self, query_dict):
        """Translates query dict of form return to default dict and removes single value lists. """

        data = {}
        for key in query_dict.keys():
            v = query_dict.getlist(key)
            if len(v) == 1:
                v = v[0]
            data[key] = v
        return data

    @staticmethod
    def get_button_line(button_name, button_label):
        """Create and return right aligned search button. """

        div = Div(
            Div(
                css_class="col-md-8"
            ),
            Div(
                Div(
                    MySubmit(button_name, button_label),
                    css_class="text-right"
                ),
                css_class="col-md-4"
            ),
            css_class="form-row"
        )
        return div


class _NdrCoreSearchForm(_NdrCoreForm):
    """Base form class for all (non-admin) NDR Core Search forms. Provides common functions for simple and
    configured search. """

    def init_simple_search_fields(self):
        """Create form fields for simple search. """

        self.fields['search_term'] = forms.CharField(label=NdrCoreValue.get_or_initialize("search_simple_field_label",
                                                                                          init_value="Search Term").value_value,
                                                     required=False,
                                                     max_length=100,
                                                     help_text=NdrCoreValue.get_or_initialize("search_simple_help_text",
                                                                                              init_value="Search for anything!").value_value)

        self.fields['and_or_field'] = forms.ChoiceField(label=_('And or Or Search'),
                                                        choices=[('and', _('AND search')), ('or', _('OR search'))],
                                                        required=False,
                                                        )

        if NdrCoreSearchConfiguration.get_simple_search_mockup_config(None).search_has_compact_result:
            self.fields['compact_view_simple'] = forms.BooleanField(required=False,
                                                                    widget=BootstrapSwitchWidget(
                                                                        attrs={'label': 'Compact Result View'}),
                                                                    label='')

    @staticmethod
    def get_simple_search_layout_fields():
        """Create and return layout fields for the simple search fields. """

        search_field = Field('search_term', wrapper_class='col-md-12')
        type_field = Field('and_or_field', wrapper_class='col-md-4')
        return search_field, type_field

    @staticmethod
    def get_search_button(conf_name):
        """Create and return right aligned search button. """
        div = Div(
            Div(
                css_class="col-md-5"
            ),
            Div(
                Field(f'compact_view_{conf_name}'),
                css_class="col-md-4"
            ),
            Div(
                Div(
                    MySubmit(f'search_button_{conf_name}', _('Search')),
                    css_class="text-right"
                ),
                css_class="col-md-3"
            ),
            css_class="form-row"
        )
        return div


class SimpleSearchForm(_NdrCoreSearchForm):
    """Form class for the simple search form. Provides a text field, an and/or option and a search button. """

    def __init__(self, *args, **kwargs):
        """Initializes the form fields."""
        super().__init__(*args, **kwargs)
        self.init_simple_search_fields()

    @property
    def helper(self):
        """Creates and returns the form helper class with the layout-ed form fields. """

        helper = FormHelper()
        helper.form_method = 'GET'
        layout = helper.layout = Layout()

        search_field, type_field = self.get_simple_search_layout_fields()
        layout.append(Div(search_field, css_class='form-row'))
        layout.append(Div(type_field, css_class='form-row'))
        layout.append(self.get_search_button('simple'))

        helper.form_show_labels = False
        return helper


class FilteredListWidget(s2forms.Select2MultipleWidget):
    # TODO: This is a copy of the original widget.
    """Widget to display a multi select2 dropdown for list configurations. """

    search_fields = [
        'list_name__icontains'
    ]


class NumberRangeField(forms.CharField):

    lowest_number = 1
    highest_number = 999999

    def __init__(self, *args, **kwargs):
        if 'lowest_number' in kwargs:
            self.lowest_number = kwargs.pop('lowest_number')
        if 'highest_number' in kwargs:
            self.highest_number = kwargs.pop('highest_number')
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        """Normalize data to a list of strings."""
        # Return an empty list if no input was given.
        if not value:
            return []

        try:
            result = set()
            for part in value.split(','):
                x = part.split('-')
                result.update(range(int(x[0]), int(x[-1]) + 1))
            return sorted(result)
        except ValueError:
            raise forms.ValidationError(_('Invalid value: Format is "1,2,3-5,7"'))

    def validate(self, value):
        """Check if value consists only of valid emails."""
        # Use the parent's handling of required fields, etc.
        super().validate(value)
        if len(value) == 0:
            return
        elif len(value) == 1:
            if value[0] < self.lowest_number or value[0] > self.highest_number:
                raise forms.ValidationError(_('Value is out of range. ({}-{})'.format(self.lowest_number, self.highest_number)))
        if len(value) > 1:
            if value[0] < self.lowest_number or value[-1] > self.highest_number:
                raise forms.ValidationError(_('Value is out of range. ({}-{})'.format(self.lowest_number, self.highest_number)))

        if value is None:
            raise forms.ValidationError(_('Invalid value'))


class AdvancedSearchForm(_NdrCoreSearchForm):
    """Form class for the advanced (=configured) search. Needs a search config and then creates and configures
    the form from it. """

    def __init__(self, *args, **kwargs):
        """Initialises  all needed form fields for the configured search based on the page's search configuration. """

        super().__init__(*args, **kwargs)

        if 'search_config' not in kwargs:
            self.search_configs = self.ndr_page.search_configs.all()
        else:
            self.search_configs = [NdrCoreSearchConfiguration.objects.get(conf_name=self.search_config_name),]

        self.query_dict = {}
        if len(args) > 0:
            self.query_dict = self.querydict_to_dict(args[0])

        if self.ndr_page is not None and self.ndr_page.page_type == NdrCorePage.PageType.COMBINED_SEARCH:
            self.init_simple_search_fields()

        for search_config in self.search_configs:
            if search_config.search_has_compact_result:
                self.fields[f'compact_view_{search_config.conf_name}'] = forms.BooleanField(required=False,
                                                                                            widget=BootstrapSwitchWidget(
                                                                                                attrs={'label': 'Compact Result View'}),
                                                                                            label='')

            for field in search_config.search_form_fields.all():
                search_field = field.search_field
                form_field = None
                help_text = mark_safe(f'<small id="{search_field.field_name}Help" class="form-text text-muted">'
                                      f'{search_field.help_text}</small>')

                # Text field
                if search_field.field_type == search_field.FieldType.STRING:
                    form_field = forms.CharField(label=search_field.field_label,
                                                 required=search_field.field_required,
                                                 help_text=help_text)
                # Number field
                if search_field.field_type == search_field.FieldType.NUMBER:
                    form_field = forms.IntegerField(label=search_field.field_label,
                                                    required=search_field.field_required,
                                                    help_text=help_text)
                # Number Range field
                if search_field.field_type == search_field.FieldType.NUMBER_RANGE:
                    form_field = NumberRangeField(label=search_field.field_label,
                                                  required=search_field.field_required,
                                                  help_text=help_text,
                                                  lowest_number=search_field.lower_value if search_field.lower_value is not None else 1,
                                                  highest_number=search_field.upper_value if search_field.upper_value is not None else 999999)
                # Boolean field (checkbox)
                if search_field.field_type == search_field.FieldType.BOOLEAN:
                    form_field = forms.BooleanField(label=search_field.field_label,
                                                    required=search_field.field_required,
                                                    help_text=help_text)
                # Date field
                if search_field.field_type == search_field.FieldType.DATE:
                    form_field = forms.DateField(label=search_field.field_label,
                                                 required=search_field.field_required,
                                                 help_text=help_text)
                # Date range field
                if search_field.field_type == search_field.FieldType.DATE_RANGE:
                    form_field = fields.DateRangeField(label=search_field.field_label,
                                                       required=search_field.field_required,
                                                       help_text=help_text,
                                                       input_formats=['%d.%m.%Y'],
                                                       widget=widgets.DateRangeWidget(
                                                           format='%d.%m.%Y',
                                                           picker_options={'startDate': "01.01.1729",
                                                                           'endDate': "31.12.1840",
                                                                           'minYear': 1729,
                                                                           'maxYear': 1840,
                                                                           "maxSpan": {
                                                                               "years": 500
                                                                           },
                                                                           'showDropdowns': True}
                                                       ))
                # List field (dropdown)
                if search_field.field_type == search_field.FieldType.LIST:
                    form_field = forms.ChoiceField(label=search_field.field_label,
                                                   choices=[('', _('Please Choose'))] + search_field.get_list_choices(),
                                                   required=search_field.field_required,
                                                   help_text=help_text)
                # Multi list field (multiple select with Select2)
                if search_field.field_type == search_field.FieldType.MULTI_LIST:
                    form_field = forms.MultipleChoiceField(label=search_field.field_label,
                                                           choices=search_field.get_list_choices(),
                                                           widget=FilteredListWidget(attrs={'data-minimum-input-length': 0}),
                                                           required=search_field.field_required,
                                                           help_text=help_text)

                # Add the field to the form if it was created.
                if form_field is not None:
                    self.fields[f'{search_config.conf_name}_{search_field.field_name}'] = form_field

    @property
    def helper(self):
        """Creates and returns the form helper class with the layout-ed form fields. """

        helper = FormHelper()
        helper.form_method = "GET"
        layout = helper.layout = Layout()

        # There can be multiple search configurations for one page. Each of them gets its own tab.
        tabs = TabHolder(css_id='id_tabs')
        # A combined search has a simple search tab as well.
        if self.ndr_page.page_type == NdrCorePage.PageType.COMBINED_SEARCH:
            tab_simple = Tab(_('Simple Search'), css_id='simple')
            search_field, type_field = self.get_simple_search_layout_fields()
            tab_simple.append(Div(search_field, css_class='form-row'))
            tab_simple.append(Div(type_field, css_class='form-row'))
            tab_simple.append(self.get_search_button('simple'))
            tabs.append(tab_simple)

        # For each search configuration, create a tab and add the form fields to it.
        for search_config in self.search_configs:
            tab = Tab(search_config.conf_label, css_id=search_config.conf_name)

            # The form fields are grouped by row and column. The row is the outer loop.
            max_row = search_config.search_form_fields.all().aggregate(Max('field_row'))
            for row in range(max_row['field_row__max']):
                row += 1
                form_row = Div(css_class='form-row')
                # The column is the inner loop.
                for column in search_config.search_form_fields.filter(field_row=row).order_by('field_column'):
                    if column.search_field.field_type == column.search_field.FieldType.INFO_TEXT:
                        form_field = Div(HTML(mark_safe(
                            f'<div class="alert alert-info small" role="alert">'
                            f'<i class="fa-regular fa-circle-info"></i>&nbsp;'
                            f'<strong>{column.search_field.field_label}</strong><br/>'
                            f"{column.search_field.list_choices}"
                            f'</div>'
                        )), css_class=f'col-md-{column.field_size}')
                    else:
                        form_field = Field(f'{search_config.conf_name}_{column.search_field.field_name}',
                                           placeholder=column.search_field.field_label,
                                           wrapper_class=f'col-md-{column.field_size}')
                        # Checkboxes are displayed inline.
                        if column.search_field.field_type == column.search_field.FieldType.BOOLEAN:
                            form_field.wrapper_class += 'custom-control-inline pt-3'
                            if column.field_column > 1:
                                form_field.wrapper_class += ' pl-5'

                    form_row.append(form_field)

                tab.append(form_row)

            tab.append(self.get_search_button(search_config.conf_name))
            tabs.append(tab)

        layout.append(tabs)

        helper.form_show_labels = True

        return helper


class FilterForm(_NdrCoreForm):
    """TODO """

    def __init__(self, *args, **kwargs):
        """TODO """

        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        """Creates and returns the form helper class with the layout-ed form fields. """
        helper = FormHelper()
        helper.form_method = "GET"
        helper.form_show_labels = False
        layout = helper.layout = Layout()
        return helper


class ContactForm(ModelForm, _NdrCoreForm):
    """TODO """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreUserMessage
        exclude = []

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)

        self.fields['message_subject'].initial = NdrCoreValue.get_or_initialize(value_name='contact_form_default_subject').get_value()
        self.fields['message_subject'].label = _('Message Subject')
        self.fields['message_ret_email'].label = _('Your E-Mail address')
        self.fields['message_text'].label = _('Message Text')

        if NdrCoreValue.get_or_initialize(value_name='contact_form_display_captcha').get_value():
            self.fields['captcha'] = ReCaptchaField()

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column('message_subject', css_class='form-group col-md-6 mb-0'),
            Column('message_ret_email', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        form_row = Row(
            Column('message_text', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        if NdrCoreValue.get_or_initialize(value_name='contact_form_display_captcha').get_value():
            form_row = Row(
                Column('captcha', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            )
            layout.append(form_row)

        layout.append(_NdrCoreForm.get_button_line('submit', _('Send Message')))

        return helper


class TestForm(_NdrCoreForm):
    """TODO """
    field_1 = forms.CharField()
    field_2 = forms.BooleanField()
    field_3 = forms.ChoiceField(choices=[('1', 'Choice'), ('2', 'Choice 2'), ('3', 'Choice 3')])


class MySubmit(BaseInput):
    """TODO """

    input_type = "submit"

    def __init__(self, *args, **kwargs):
        """TODO """

        self.field_classes = "btn btn-primary w-100"
        super().__init__(*args, **kwargs)
