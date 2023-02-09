import csv
import os

from captcha.fields import ReCaptchaField
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column, Div, BaseInput, ButtonHolder, Submit
from django import forms
from django.conf import settings
from django.db.models import Max
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from ndr_core.models import NdrCoreValue, NdrCorePage, NdrCoreUserMessage
from ndr_core.widgets import CustomSelect


class _NdrCoreForm(forms.Form):
    """Base form class for all (non-admin) NDR Core forms.  """

    ndr_page = None

    def __init__(self, *args, **kwargs):
        """Init the form class. Save the ndr page if it is provided."""
        if 'ndr_page' in kwargs:
            self.ndr_page = kwargs.pop('ndr_page')
        if 'instance' in kwargs:
            kwargs.pop('instance')

        super(forms.Form, self).__init__(*args, **kwargs)


class _NdrCoreSearchForm(_NdrCoreForm):
    """Base form class for all (non-admin) NDR Core Search forms. Provides common functions for simple and
    configured search. """

    def init_simple_search_fields(self):
        """Create form fields for simple search. """

        self.fields['search_term'] = forms.CharField(label=NdrCoreValue.get_or_initialize("search_simple_field_label",
                                                                                          init_value="Search Term"),
                                                     required=False,
                                                     max_length=100,
                                                     help_text=NdrCoreValue.get_or_initialize("search_simple_help_text",
                                                                                              init_value="Search for anything!"))

        self.fields['and_or_field'] = forms.ChoiceField(label=_('And or Or Search'),
                                                        choices=[('and', _('AND search')), ('or', _('OR search'))],
                                                        required=False,
                                                        )

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
                    css_class="col-md-8"
                    ),
                Div(
                    Div(
                        MySubmit(f'search_button_{conf_name}', _('Search')),
                        css_class="text-right"
                    ),
                    css_class="col-md-4"
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


class AdvancedSearchForm(_NdrCoreSearchForm):
    """Form class for the advanced (=configured) search. Needs a search config and then creates and configures
    the form from it. """

    def __init__(self, *args, **kwargs):
        """Initialises  all needed form fields for the configured search based on the page's search configuration. """

        super().__init__(*args, **kwargs)

        self.search_configs = self.ndr_page.search_configs.all()

        self.query_dict = {}
        if len(args) > 0:
            self.query_dict = querydict_to_dict(args[0])

        if self.ndr_page.page_type == NdrCorePage.PageType.COMBINED_SEARCH:
            self.init_simple_search_fields()

        for search_config in self.search_configs:
            for field in search_config.search_form_fields.all():
                search_field = field.search_field
                form_field = None
                help_text = mark_safe(f'<small id="{search_field.field_name}Help" class="form-text text-muted">'
                                      f'{search_field.help_text}</small>')

                if search_field.field_type == search_field.FieldType.STRING:
                    form_field = forms.CharField(label=search_field.field_label,
                                                 required=search_field.field_required, help_text=help_text)
                if search_field.field_type == search_field.FieldType.NUMBER:
                    form_field = forms.IntegerField(label=search_field.field_label,
                                                    required=search_field.field_required, help_text=help_text)
                if search_field.field_type == search_field.FieldType.BOOLEAN:
                    form_field = forms.BooleanField(label=search_field.field_label,
                                                    required=search_field.field_required, help_text=help_text)
                if search_field.field_type == search_field.FieldType.DATE:
                    form_field = forms.DateField(label=search_field.field_label,
                                                 required=search_field.field_required, help_text=help_text)
                if search_field.field_type == search_field.FieldType.DICTIONARY:
                    form_field = forms.ChoiceField(label=search_field.field_label,
                                                   choices=[],
                                                   required=search_field.field_required, help_text=help_text)
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

        self.query_dict = {}
        if len(args) > 0:
            self.query_dict = querydict_to_dict(args[0])

        if "tags[]" in self.query_dict:
            selection = self.query_dict["tags[]"]
            if selection == '':
                selection = []
            elif isinstance(selection, str):
                selection = [selection, ]
        else:
            selection = []

        choice_widget = CustomSelect(attrs={'list_name': 'tags',
                                            'selection': selection,
                                            'placeholder': 'All sub collections are selected. '
                                                           'Filter them by type here.'}, )
        dict_config = {
            "type": "tsv",
            "file": "main/tag_list.tsv",
            "search_column": 0,
            "display_column": 1,
            "has_title_row": True
        }
        choices = get_choices_from_tsv(dict_config)
        filter_field = forms.ChoiceField(widget=choice_widget, choices=choices, required=False)
        self.fields['tags'] = filter_field

    @property
    def helper(self):
        """Creates and returns the form helper class with the layout-ed form fields. """

        helper = FormHelper()
        helper.form_method = "GET"
        helper.form_show_labels = False
        layout = helper.layout = Layout()

        form_row = Row(
            Column(
                Field('tags'),
                css_class=f'col-md-10'
            ),
            Column(
                Div(
                    MySubmit('filter', _('Filter')),
                    MySubmit('show_all', _('Show all')),
                    css_class="btn-group d-flex"
                ),
                css_class=f'col-md-2'
            ),
        )

        layout.append(form_row)
        return helper


class ContactForm(ModelForm, _NdrCoreForm):
    """TODO """

    captcha = ReCaptchaField()

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

        form_row = Row(
            Column('captcha', css_class='form-group col-md-12 mb-0'),
            css_class='form-row'
        )
        layout.append(form_row)

        bh = ButtonHolder(
            Submit('submit', "Send Message", css_class='btn-default'),
            css_class="modal-footer"
        )
        layout.append(bh)

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

        self.field_classes = "btn btn btn-outline-secondary w-100"
        super().__init__(*args, **kwargs)


def get_choices_from_tsv(dict_config):
    """TODO """

    if "display_column" in dict_config and "search_column" in dict_config and "file" in dict_config:
        choices = list()
        with open(os.path.join(settings.STATIC_ROOT, dict_config["file"]), encoding='utf-8') as fd:
            rd = csv.reader(fd, delimiter="\t")
            line = 0
            for row in rd:
                if line > 0 or (line == 0 and not dict_config["has_title_row"]):
                    choices.append((
                        row[dict_config["search_column"]],
                        row[dict_config["display_column"]]
                    ))
                line += 1
        choices = sorted(choices, key=lambda tup: tup[1])
        return choices
    else:
        print(">> dictionary config needs search- and display-column")
        return []


def querydict_to_dict(query_dict):
    """Translates query dict of form return to default dict and removes single value lists. """

    data = {}
    for key in query_dict.keys():
        v = query_dict.getlist(key)
        if len(v) == 1:
            v = v[0]
        data[key] = v
    return data

