import csv
import os

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Row, Column, Div, Button, BaseInput, Fieldset, HTML
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Max
from django.utils.safestring import mark_safe

from ndr_core.models import SearchConfiguration, SearchFieldFormConfiguration, NdrCoreValue
from ndr_core.widgets import CustomSelect, CustomRange


class _NdrCoreForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)


class SimpleSearchForm(_NdrCoreForm):
    search_term = forms.CharField(label='Search Term', max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        helper = FormHelper()
        helper.add_input(Submit('search', 'Search'))
        return helper


class AdvancedSearchForm(_NdrCoreForm):

    config = None
    repo_to_search = forms.Field()

    def __init__(self, config: SearchConfiguration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

        self.query_dict = {}
        if len(args) > 0:
            self.query_dict = querydict_to_dict(args[0])

        for field in self.config.search_form_fields.all():
            search_field = field.search_field
            form_field = None
            help_text = mark_safe(f'<small id="{search_field.field_name}Help" class="form-text text-muted">'
                                  f'{search_field.help_text}</small>')

            if search_field.field_type == search_field.FieldType.STRING:
                form_field = forms.CharField(required=search_field.field_required, help_text=help_text)
            if search_field.field_type == search_field.FieldType.NUMBER:
                form_field = forms.IntegerField(required=search_field.field_required, help_text=help_text)

            if form_field is not None:
                self.fields[field] = form_field

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = "GET"
        layout = helper.layout = Layout()

        max_row = self.config.search_form_fields.aaggregate(Max('field_row'))
        for row in range(max_row['field_row__max']):
            form_row = Div(css_class='form-row')
            for column in self.config.search_form_fields.filter(field_row=row).order_by('field_column'):
                form_field = Field(column.search_field.field_name, placeholder=column.search_field.field_label,
                                   wrapper_class=f'col-md-{column.field_size}')
                form_row.append(form_field)
            layout.append(form_row)

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

        choice_widget = CustomSelect(attrs={'list_name': 'tags', 'selection': selection, 'placeholder': 'All sub collections are selected. Filter them by type here.'}, )
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
    email = forms.EmailField(label='Your E-Mail Address', help_text="We are going to reply to this e-mail address.", required=True)
    message = forms.CharField(label="Message",
                              help_text='Please be as specific as you can in your message. It will help us to answer your questions!',
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


class NdrCoreLoginForm(AuthenticationForm):
    """Takes Django's login form and adds an input to it so it can be rendered with crispy forms """

    def __init__(self, *args, **kwargs):
        super(NdrCoreLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(MySubmit('login', 'Login'))
