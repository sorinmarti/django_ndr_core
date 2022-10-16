import csv
import os

from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Column, Div, BaseInput, HTML
from django import forms
from django.conf import settings
from django.db.models import Max
from django.utils.safestring import mark_safe

from ndr_core.models import NdrCoreValue, NdrCorePage
from ndr_core.widgets import CustomSelect


class _NdrCoreForm(forms.Form):
    """TODO """

    ndr_page = None

    def __init__(self, *args, **kwargs):
        if 'ndr_page' in kwargs:
            self.ndr_page = kwargs.pop('ndr_page')

        super(forms.Form, self).__init__(*args, **kwargs)

    def init_simple_search_fields(self):
        self.fields['search_term'] = forms.CharField(label='Search Term',
                                                     required=False,
                                                     max_length=100,
                                                     help_text="Search for anything!")

        self.fields['and_or_field'] = forms.ChoiceField(label='And or Or Search',
                                                        choices=[('and', 'AND search'), ('or', 'OR search')],
                                                        required=False,
                                                        )

    def get_simple_search_layout_fields(self):
        search_field = Field('search_term',
                             wrapper_class='col-md-12')
        type_field = Field('and_or_field',
                           wrapper_class='col-md-4')

        return search_field, type_field

    def get_search_button(self, conf_name):
        div = Div(
                Div(css_class="col-md-8"),
                Div(Div(MySubmit(f'search_button_{conf_name}', 'Search'), css_class="text-right"),
                    css_class="col-md-4"),
                css_class="form-row")
        return div


class SimpleSearchForm(_NdrCoreForm):
    """TODO """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_simple_search_fields()

    @property
    def helper(self):
        helper = FormHelper()
        layout = helper.layout = Layout()

        search_field, type_field = self.get_simple_search_layout_fields()
        layout.append(Div(search_field, css_class='form-row'))
        layout.append(Div(type_field, css_class='form-row'))
        layout.append(self.get_search_button('simple'))

        helper.form_show_labels = False
        return helper


class AdvancedSearchForm(_NdrCoreForm):
    """TODO """

    def __init__(self, *args, **kwargs):
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
                    form_field = forms.CharField(required=search_field.field_required, help_text=help_text)
                if search_field.field_type == search_field.FieldType.NUMBER:
                    form_field = forms.IntegerField(required=search_field.field_required, help_text=help_text)

                if form_field is not None:
                    self.fields[f'{search_config.conf_name}_{search_field.field_name}'] = form_field

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = "GET"
        layout = helper.layout = Layout()

        # Add "new search" buttons
        """layout.append(
            Div(
                Div(
                    Div(
                        HTML('<a href="#" type="button" class="btn btn-sm btn-outline-secondary ">refine search</a>'),
                        HTML('<a href="#" type="button" class="btn btn-sm btn-outline-secondary ">start a new search</a>'),
                        css_class="btn-group float-right"),
                    css_class="col-12"),
                css_class="form-row")
        )"""

        tabs = TabHolder(css_id='id_tabs')
        if self.ndr_page.page_type == NdrCorePage.PageType.COMBINED_SEARCH:
            tab_simple = Tab('Simple Search', css_id='simple')
            search_field, type_field = self.get_simple_search_layout_fields()
            tab_simple.append(Div(search_field, css_class='form-row'))
            tab_simple.append(Div(type_field, css_class='form-row'))
            tab_simple.append(self.get_search_button('simple'))
            tabs.append(tab_simple)

        for search_config in self.search_configs:
            tab = Tab(search_config.conf_label, css_id=search_config.conf_name)

            max_row = search_config.search_form_fields.all().aggregate(Max('field_row'))
            for row in range(max_row['field_row__max']):
                row += 1
                form_row = Div(css_class='form-row')
                for column in search_config.search_form_fields.filter(field_row=row).order_by('field_column'):
                    form_field = Field(f'{search_config.conf_name}_{column.search_field.field_name}', placeholder=column.search_field.field_label,
                                       wrapper_class=f'col-md-{column.field_size}')
                    form_row.append(form_field)

                tab.append(form_row)

            tab.append(self.get_search_button(search_config.conf_name))
            tabs.append(tab)

        layout.append(tabs)

        helper.form_show_labels = False

        return helper


class FilterForm(_NdrCoreForm):

    def __init__(self, *args, **kwargs):
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
                    MySubmit('filter', 'Filter'),
                    MySubmit('show_all', 'Show all'),
                    css_class="btn-group d-flex"
                ),
                css_class=f'col-md-2'
            ),
        )

        layout.append(form_row)
        return helper


class ContactForm(_NdrCoreForm):
    """TODO """

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(MySubmit('submit', 'Send Message'))

        self.fields['subject'].initial = NdrCoreValue.objects.get(value_name='contact_form_default_subject').value_value

    subject = forms.CharField(label='Subject',
                              initial='',
                              help_text="You can change the subject.",
                              required=True)

    email = forms.EmailField(label='Your E-Mail Address',
                             help_text="We are going to reply to this e-mail address.",
                             required=True)

    message = forms.CharField(label="Message",
                              help_text='Please be as specific as you can in your message. '
                                        'It will help us to answer your questions!',
                              widget=forms.Textarea)


class MySubmit(BaseInput):
    input_type = "submit"

    def __init__(self, *args, **kwargs):
        self.field_classes = "btn btn btn-outline-secondary w-100"
        super().__init__(*args, **kwargs)


def get_choices_from_tsv(dict_config):
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
    data = {}
    for key in query_dict.keys():
        v = query_dict.getlist(key)
        if len(v) == 1:
            v = v[0]
        data[key] = v
    return data