"""Contains forms used in the NDRCore admin interface for the creation or edit of Search form configurations."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, HTML
from django import forms
from django.core.exceptions import ValidationError

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreSearchConfiguration


class SearchConfigurationForm(forms.ModelForm):
    """Form to create or edit a search configuration search form. """

    # ------------------------------------------------------------------ #
    # Non-model fields: MongoDB API-specific settings.                    #
    # These are serialised into / deserialised from api_settings['mongodb']
    # ------------------------------------------------------------------ #

    mongodb_use_atlas_search = forms.BooleanField(
        required=False,
        label="Use Atlas Search",
        help_text="Enable MongoDB Atlas $search instead of regex for simple search.",
    )
    mongodb_atlas_index = forms.CharField(
        required=False,
        label="Atlas Search Index",
        initial='default',
        help_text="Name of the Atlas Search index (default: 'default').",
    )
    mongodb_atlas_fuzzy = forms.BooleanField(
        required=False,
        label="Fuzzy Matching",
        help_text="Tolerate typos using fuzzy matching.",
    )
    mongodb_atlas_fuzzy_max_edits = forms.IntegerField(
        required=False,
        label="Max Edits",
        initial=1,
        min_value=1,
        max_value=2,
        help_text="Maximum Levenshtein edit distance (1 or 2). Only used when fuzzy is enabled.",
    )
    mongodb_atlas_sort_by_relevance = forms.BooleanField(
        required=False,
        label="Sort by Relevance",
        initial=True,
        help_text="Sort results by Atlas Search relevance score. When unchecked, uses the Sort Field above.",
    )
    mongodb_atlas_highlighting = forms.BooleanField(
        required=False,
        label="Enable Highlighting",
        help_text="Inject matched text fragments as _hl.field.path in each result. "
                  "Use {_hl.content.raw_text|default:} in result card templates.",
    )
    mongodb_atlas_autocomplete_path = forms.CharField(
        required=False,
        label="Autocomplete Field",
        help_text="Field path for autocomplete suggestions (e.g. actor.entity_canonical). "
                  "Must be indexed with type: autocomplete in Atlas.",
    )

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreSearchConfiguration
        fields = ['conf_name', 'conf_label',
                  'api_type', 'api_connection_url',
                  'api_user_name', 'api_password', 'api_auth_key',
                  'search_id_field', 'sort_field', 'sort_order',
                  'search_has_compact_result', 'compact_result_is_default', 'page_size',
                  'citation_expression', 'repository_url',
                  'has_simple_search', 'simple_search_first', 'simple_query_main_field',
                  'simple_query_label', 'simple_query_help_text', 'simple_search_tab_title',
                  'manifest_relation_expression', 'manifest_page_expression']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate MongoDB non-model fields from api_settings on an existing instance
        if self.instance and self.instance.pk:
            mongodb_settings = (self.instance.api_settings or {}).get('mongodb', {})
            self.fields['mongodb_use_atlas_search'].initial = mongodb_settings.get('use_atlas_search', False)
            self.fields['mongodb_atlas_index'].initial = mongodb_settings.get('atlas_search_index', 'default')
            self.fields['mongodb_atlas_fuzzy'].initial = mongodb_settings.get('atlas_search_fuzzy', False)
            self.fields['mongodb_atlas_fuzzy_max_edits'].initial = mongodb_settings.get('atlas_search_fuzzy_max_edits', 1)
            self.fields['mongodb_atlas_sort_by_relevance'].initial = mongodb_settings.get('atlas_sort_by_relevance', True)
            self.fields['mongodb_atlas_highlighting'].initial = mongodb_settings.get('atlas_highlighting', False)
            self.fields['mongodb_atlas_autocomplete_path'].initial = mongodb_settings.get('atlas_autocomplete_path', '')

    def save(self, commit=True):
        instance = super().save(commit=False)
        api_settings = dict(instance.api_settings) if instance.api_settings else {}

        # Persist MongoDB-specific settings under the 'mongodb' key
        api_settings['mongodb'] = {
            'use_atlas_search': self.cleaned_data.get('mongodb_use_atlas_search', False),
            'atlas_search_index': self.cleaned_data.get('mongodb_atlas_index') or 'default',
            'atlas_search_fuzzy': self.cleaned_data.get('mongodb_atlas_fuzzy', False),
            'atlas_search_fuzzy_max_edits': self.cleaned_data.get('mongodb_atlas_fuzzy_max_edits') or 1,
            'atlas_sort_by_relevance': self.cleaned_data.get('mongodb_atlas_sort_by_relevance', True),
            'atlas_highlighting': self.cleaned_data.get('mongodb_atlas_highlighting', False),
            'atlas_autocomplete_path': self.cleaned_data.get('mongodb_atlas_autocomplete_path', ''),
        }
        instance.api_settings = api_settings

        if commit:
            instance.save()
            self.save_m2m()
        return instance

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        form_row = Row(
            Column(Div(HTML('''
            <br/>
            <b>1.) Provide a name and a label for your configuration</b>
            &nbsp;&nbsp;
            <small>(Keep the name short and avoid special characters!))</small>
            <hr/>
            ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('conf_name', css_class='col-6'),
            Column('conf_label', css_class='col-6'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column(Div(HTML('''
                    <br/>
                    <b>2.) Configure the access to your data</b>
                    &nbsp;&nbsp;
                    <small>(Select a type to see how to compose the connection string)</small>
                    <hr/>
                    ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('api_type', css_class='col-4'),
            Column('api_connection_url', css_class='col-8'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('api_user_name', css_class='col-3'),
            Column('api_password', css_class='col-3'),
            Column('api_auth_key', css_class='col-6'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column(Div(HTML('''
                            <br/>
                            <b>3.) Provide search configuration</b>
                            &nbsp;&nbsp;
                            <small>()</small>
                            <hr/>
                            ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('search_id_field', css_class='col-4'),
            Column('sort_field', css_class='col-4'),
            Column('sort_order', css_class='col-4'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('search_has_compact_result', css_class='col-3'),
            Column('page_size', css_class='col-2'),
            Column('repository_url', css_class='col-7'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('compact_result_is_default', css_class='col-3'),
            Column('citation_expression', css_class='col-9'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column(Div(HTML('''
                                    <br/>
                                    <b>4.) Simple Search</b>
                                    &nbsp;&nbsp;
                                    <small>(Check the box if you want a single
                                    field search with your search form.)</small>
                                    <hr/>
                                    ''')), css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('has_simple_search', css_class='col-4'),
            Column('simple_search_first', css_class='col-4'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('simple_query_main_field', css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('simple_query_label', css_class='col-6'),
            Column('simple_search_tab_title', css_class='col-6'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('simple_query_help_text', css_class='col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('manifest_relation_expression', css_class='col-8'),
            Column('manifest_page_expression', css_class='col-4'),
            css_class='row g-2'
        )
        layout.append(form_row)

        # ------------------------------------------------------------------ #
        # Section 5: API-specific settings                                    #
        # Each API type gets its own sub-section, shown/hidden via JS.        #
        # ------------------------------------------------------------------ #

        layout.append(Row(
            Column(Div(HTML('''
                <br/>
                <b>5.) API-specific Settings</b>
                &nbsp;&nbsp;
                <small>(Options that apply only to the selected API type.)</small>
                <hr/>
            ''')), css_class='col-12'),
            css_class='row g-2'
        ))

        # MongoDB Atlas Search sub-section
        layout.append(
            Div(
                HTML('''
                    <p class="text-muted small mb-2">
                        <strong>MongoDB — Atlas Search</strong><br>
                        When enabled, the <em>Main field</em> above is used as the search path
                        (comma-separated for multi-field, e.g.
                        <code>actor.entity_canonical,content.raw_text</code>).
                        Regex search is used when disabled.
                    </p>
                '''),
                Row(
                    Column('mongodb_use_atlas_search', css_class='col-3'),
                    Column('mongodb_atlas_index', css_class='col-9'),
                    css_class='row g-2'
                ),
                Row(
                    Column('mongodb_atlas_fuzzy', css_class='col-3'),
                    Column('mongodb_atlas_fuzzy_max_edits', css_class='col-3'),
                    css_class='row g-2'
                ),
                HTML('<hr class="my-2"/>'),
                Row(
                    Column('mongodb_atlas_sort_by_relevance', css_class='col-4'),
                    Column('mongodb_atlas_highlighting', css_class='col-4'),
                    css_class='row g-2'
                ),
                HTML('''
                    <p class="text-muted small mt-1 mb-1">
                        Highlighting injects matched fragments into each result as
                        <code>_hl.field.path</code>. Use
                        <code>{_hl.content.raw_text|default:}</code> in result card templates.
                    </p>
                '''),
                Row(
                    Column('mongodb_atlas_autocomplete_path', css_class='col-12'),
                    css_class='row g-2'
                ),
                css_id='api-settings-mongodb',
                style='display:none;',
            )
        )

        # JS: show the relevant sub-section based on the selected api_type
        layout.append(HTML('''
            <script>
            (function () {
                var select = document.getElementById('id_api_type');
                function toggle() {
                    var val = select ? select.value : '';
                    var mongodb = document.getElementById('api-settings-mongodb');
                    if (mongodb) mongodb.style.display = (val === 'mongodb') ? 'block' : 'none';
                }
                if (select) {
                    select.addEventListener('change', toggle);
                    toggle();
                }
            })();
            </script>
        '''))

        return helper

    def clean_conf_name(self):
        """Check if conf_name is not a reserved name. """
        data = self.cleaned_data['conf_name']
        if data == 'simple':
            raise ValidationError("'simple' is a reserved term and can't be used")
        return data


class SearchConfigurationCreateForm(SearchConfigurationForm):
    """Form to create a search field form. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Search Configuration'))
        return helper


class SearchConfigurationEditForm(SearchConfigurationForm):
    """Form to edit an existing search configuration.

    conf_name is disabled because it is the primary key — changing it would
    create a duplicate instead of updating the existing record.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['conf_name'].disabled = True
        self.fields['conf_name'].help_text = "The configuration name cannot be changed after creation."

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save Search Configuration'))
        return helper


class ExampleResultForm(forms.ModelForm):
    """Form to set the example result JSON for a search configuration."""

    class Meta:
        model = NdrCoreSearchConfiguration
        fields = ['example_result_json']
        widgets = {
            'example_result_json': forms.Textarea(attrs={
                'rows': 20,
                'class': 'form-control font-monospace',
                'placeholder': '{\n  "id": "example_001",\n  "title": "Example Record"\n}',
                'id': 'id_example_result_json',
            }),
        }

    def clean_example_result_json(self):
        """Accept raw JSON text and parse it."""
        import json
        raw = self.data.get('example_result_json_raw', '').strip()
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}")

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_method = 'POST'
        layout = helper.layout = Layout()

        layout.append(Div(
            HTML('<div class="alert alert-info">'
                 '<strong><i class="fa-regular fa-circle-info"></i> Example Result JSON:</strong> '
                 'Paste a single record from your API response here (not the full paginated response, '
                 'just one <code>{ ... }</code> object). '
                 'NDR Core will extract all available field paths and use them as hints in the result '
                 'field editor and for live preview.'
                 '</div>'),
            css_class='mb-3'
        ))

        layout.append(Row(
            Column(
                HTML('<label class="form-label fw-bold">JSON</label>'
                     '<div id="ndr-json-error" class="text-danger small mb-1 d-none"></div>'),
                HTML('<textarea id="id_example_result_json_raw" name="example_result_json_raw" '
                     'rows="22" class="form-control font-monospace" '
                     'placeholder=\'{ "id": "example_001", "title": "Example Record" }\'>'
                     '</textarea>'),
                css_class='form-group col-12'
            ),
            css_class='row g-2'
        ))

        layout.append(get_form_buttons('Save Example JSON'))
        return helper
