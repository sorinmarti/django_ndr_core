"""Form classes for the search."""
from bootstrap_daterangepicker.fields import DateRangeField
from bootstrap_daterangepicker.widgets import DateRangeWidget
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, HTML
from django import forms
from django.db.models import Max
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _, get_language

from ndr_core.models import NdrCoreTranslation
from ndr_core.forms.fields import NumberRangeField
from ndr_core.forms.forms_base import _NdrCoreForm
from ndr_core.forms.widgets import (
    BootstrapSwitchWidget,
    NdrCoreFormSubmit,
    NdrCoreFilterButton,
    NdrCoreClearButton,
    FilteredListWidget
)


class DataListSearchForm(_NdrCoreForm):
    search_config = None

    def __init__(self, *args, **kwargs):
        if "ndr_page" in kwargs:
            self.ndr_page = kwargs.pop("ndr_page")

        if self.ndr_page is not None:
            self.search_config = self.ndr_page.search_configs.first()

        if self.search_config is None:
            raise AttributeError("No Search Config Found")

        super().__init__(*args, **kwargs)

        self.fields["search_term"] = forms.CharField(
            label=mark_safe(self.search_config.simple_query_label + "&nbsp;"),
            required=False,
            max_length=100,
            help_text=self.search_config.simple_query_help_text)


    @property
    def helper(self):
        """Creates and returns the form helper class with the layout-ed form fields."""

        helper = FormHelper()
        helper.form_method = "GET"
        layout = helper.layout = Layout()

        # Add the search field with filter and clear buttons inline
        layout.append(Field("search_term"))
        layout.append(Div(
            NdrCoreFilterButton(_("Filter")),
            HTML("&nbsp;"),
            NdrCoreClearButton(_("Clear")),
            css_class="d-flex justify-content-end gap-2 mt-2"
        ))

        return helper



class AdvancedSearchForm(_NdrCoreForm):
    """Form class for the search.
    Needs a search config and then creates and configures the form from it."""

    search_configs = None
    combined_simple_config = None

    def __init__(self, *args, **kwargs):
        """Initializes all needed form fields for the configured search based on
        the page's search configuration."""

        if "ndr_page" in kwargs:
            self.ndr_page = kwargs.pop("ndr_page")

        if self.ndr_page is not None:
            self.search_configs = self.ndr_page.search_configs.all()
            self.combined_simple_config = getattr(self.ndr_page, 'combined_simple_search_config', None)
        elif "search_config" in kwargs:
            self.search_configs = [kwargs.pop("search_config")]
            self.combined_simple_config = None
        else:
            raise AttributeError("No Search Config Found")

        super().__init__(*args, **kwargs)

        self.query_dict = {}
        if len(args) > 0:
            self.query_dict = self.query_dict_to_dict(args[0])

        # If a combined simple search master config is set, add ONE combined simple tab field.
        if self.combined_simple_config:
            self.init_combined_simple_search_fields(self.combined_simple_config)

        # Search Form is composed of different search configurations. Each of them has its own tab.
        # A search configuration may have a simple search tab as well.
        for search_config in self.search_configs:
            # Per-config simple tabs are suppressed when combined mode is active.
            if search_config.has_simple_search and not self.combined_simple_config:
                self.init_simple_search_fields(search_config)

            # If the search configuration has an advanced search tab, add the fields to the form.
            if search_config.search_has_compact_result:
                self.fields[
                    f"compact_view_{search_config.conf_name}"
                ] = self.get_compact_view_field(search_config)

            # Add the fields of the search configuration to the form.
            for field in search_config.search_form_fields.all():
                search_field = field.search_field
                form_field = None
                condition_form_field = None
                operator_form_field = None
                help_text = mark_safe(
                    f'<small id="{search_field.field_name}Help" class="form-text text-muted">'
                    f"{search_field.help_text}</small>"
                )

                # Text field
                if search_field.field_type == search_field.FieldType.STRING:
                    form_field = forms.CharField(
                        label=search_field.field_label,
                        required=search_field.field_required,
                        help_text=help_text,
                        initial=search_field.get_initial_value(),
                    )
                    # Add operator dropdown if CHOOSE
                    if search_field.comparison_operator == 'CHOOSE':
                        operator_form_field = forms.ChoiceField(
                            label=mark_safe('&nbsp;'),
                            choices=[('=', _('Exact')), ('contains', _('Contains'))],
                            initial='contains',
                            required=False,
                            widget=forms.Select(attrs={'style': 'height: 32px; font-size: 14px;'}),
                            help_text='<small class="form-text text-muted">'
                                      '  {exact_text}<br/>'
                                      '  {contains_text}'
                                      '</small>'.format(exact_text=_('Exact: exact match'),
                                                       contains_text=_('Contains: uses regex')))
                # Number field
                if search_field.field_type == search_field.FieldType.NUMBER:
                    form_field = forms.IntegerField(
                        label=search_field.field_label,
                        required=search_field.field_required,
                        help_text=help_text,
                        initial=search_field.get_initial_value(),
                    )
                    # Add operator dropdown if CHOOSE
                    if search_field.comparison_operator == 'CHOOSE':
                        operator_form_field = forms.ChoiceField(
                            label=mark_safe('&nbsp;'),
                            choices=[('=', '='), ('>', '>'), ('<', '<'), ('>=', '≥'), ('<=', '≤'), ('!=', '≠')],
                            initial='=',
                            required=False,
                            widget=forms.Select(attrs={'style': 'height: 32px; font-size: 14px;'}),
                            help_text='<small class="form-text text-muted">Comparison operator</small>')
                # Float field
                if search_field.field_type == search_field.FieldType.FLOAT:
                    form_field = forms.FloatField(
                        label=search_field.field_label,
                        required=search_field.field_required,
                        help_text=help_text,
                        initial=search_field.get_initial_value(),
                    )
                    # Add operator dropdown if CHOOSE
                    if search_field.comparison_operator == 'CHOOSE':
                        operator_form_field = forms.ChoiceField(
                            label=mark_safe('&nbsp;'),
                            choices=[('=', '='), ('>', '>'), ('<', '<'), ('>=', '≥'), ('<=', '≤'), ('!=', '≠')],
                            initial='=',
                            required=False,
                            widget=forms.Select(attrs={'style': 'height: 32px; font-size: 14px;'}),
                            help_text='<small class="form-text text-muted">Comparison operator</small>')
                # Number Range field
                if search_field.field_type == search_field.FieldType.NUMBER_RANGE:
                    form_field = NumberRangeField(
                        label=search_field.field_label,
                        required=search_field.field_required,
                        help_text=help_text,
                        lowest_number=int(search_field.lower_value)
                        if search_field.lower_value is not None
                        else 0,
                        highest_number=int(search_field.upper_value)
                        if search_field.upper_value is not None
                        else 999999,
                        initial=search_field.get_initial_value(),
                    )
                # Boolean field (checkbox)
                if search_field.field_type == search_field.FieldType.BOOLEAN:
                    form_field = forms.BooleanField(
                        label=mark_safe("&nbsp;"),
                        required=search_field.field_required,
                        help_text=help_text,
                        widget=BootstrapSwitchWidget(
                            attrs={"label": search_field.field_label}
                        ),
                        initial=search_field.get_initial_value(),
                    )
                if search_field.field_type == search_field.FieldType.BOOLEAN_LIST:
                    form_field = forms.MultipleChoiceField(
                        label=search_field.field_label,
                        choices=search_field.get_choices(),
                        required=search_field.field_required,
                        help_text=help_text,
                        initial=search_field.get_initial_value(),
                        widget=forms.CheckboxSelectMultiple,
                    )

                # Date field
                if search_field.field_type == search_field.FieldType.DATE:
                    form_field = forms.DateField(
                        label=search_field.field_label,
                        required=search_field.field_required,
                        help_text=help_text,
                        initial=search_field.get_initial_value(),
                    )
                    # Add operator dropdown if CHOOSE
                    if search_field.comparison_operator == 'CHOOSE':
                        operator_form_field = forms.ChoiceField(
                            label=mark_safe('&nbsp;'),
                            choices=[('=', _('At')), ('>', _('After')), ('<', _('Before')),
                                   ('>=', _('At or after')), ('<=', _('At or before'))],
                            initial='=',
                            required=False,
                            widget=forms.Select(attrs={'style': 'height: 32px; font-size: 14px;'}),
                            help_text='<small class="form-text text-muted">Date comparison</small>')
                # Date range field
                if search_field.field_type == search_field.FieldType.DATE_RANGE:
                    # search_field.lower_value is in the form YYYY-MM-DD. Convert it to DD.MM.YYYY
                    lower_value = search_field.lower_value
                    if lower_value is not None:
                        lower_value = (
                            f"{lower_value[8:10]}.{lower_value[5:7]}.{lower_value[0:4]}"
                        )
                    else:
                        lower_value = "01.01.2024"

                    # Do the same with upper_value
                    upper_value = search_field.upper_value
                    if upper_value is not None:
                        upper_value = (
                            f"{upper_value[8:10]}.{upper_value[5:7]}.{upper_value[0:4]}"
                        )

                    form_field = DateRangeField(
                        label=search_field.field_label,
                        required=search_field.field_required,
                        help_text=help_text,
                        input_formats=["%d.%m.%Y"],
                        widget=DateRangeWidget(
                            format="%d.%m.%Y",
                            picker_options={
                                "startDate": lower_value,
                                "endDate": "upper_value",
                                "minYear": int(lower_value[6:10] if lower_value else "1900"),
                                "maxYear": int(upper_value[6:10] if upper_value else "2100"),
                                "maxSpan": {"years": 500},
                                "showDropdowns": True,
                            },
                        ),
                        initial=search_field.get_initial_value(),
                    )
                # List field (dropdown)
                if search_field.field_type == search_field.FieldType.LIST:
                    form_field = forms.ChoiceField(
                        label=search_field.field_label,
                        choices=search_field.get_choices(null_choice=True),
                        required=search_field.field_required,
                        help_text=help_text,
                        initial=search_field.get_initial_value(),
                    )
                # Multi list field (multiple select with Select2)
                if search_field.field_type == search_field.FieldType.MULTI_LIST:
                    form_field = forms.MultipleChoiceField(
                        label=search_field.field_label,
                        choices=search_field.get_choices(),
                        widget=FilteredListWidget(
                            attrs={"data-minimum-input-length": 0}
                        ),
                        required=search_field.field_required,
                        help_text=help_text,
                        initial=search_field.get_initial_value(),
                    )
                    if search_field.list_condition == 'CHOOSE':
                        condition_form_field = forms.ChoiceField(label=mark_safe('&nbsp;'),
                                                                 choices=[('AND', _('AND')),
                                                                          ('OR', _('OR'))],
                                                                 required=False,
                                                                 widget=forms.Select(attrs={'style': 'height: 32px; font-size: 14px;'}),
                                                                 help_text='<small class="form-text text-muted">'
                                                                           '  {and_text}<br/>'
                                                                           '  {or_text}'
                                                                           '</small>'.format(and_text=_('AND: all.'),
                                                                                             or_text=_('OR: at least one.')))

                # Add the field to the form if it was created.
                if form_field is not None:
                    if not search_field.show_label:
                        form_field.label = ''
                    self.fields[
                        f"{search_config.conf_name}_{search_field.field_name}"
                    ] = form_field
                    # Add the condition field to the form if it was created.
                    if condition_form_field is not None:
                        self.fields[
                            f"{search_config.conf_name}_{search_field.field_name}_condition"
                        ] = condition_form_field
                    # Add the operator field to the form if it was created.
                    if operator_form_field is not None:
                        self.fields[
                            f"{search_config.conf_name}_{search_field.field_name}_operator"
                        ] = operator_form_field

    @staticmethod
    def get_compact_view_field(search_config):
        """Returns the compact view field for the given search configuration."""
        return forms.BooleanField(
            required=False,
            widget=BootstrapSwitchWidget(attrs={"label": _("Compact Result View")}),
            label="",
            initial=search_config.compact_result_is_default
        )

    def init_simple_search_fields(self, search_config):
        """Create form fields for simple search."""

        self.fields[f"search_term_{search_config.conf_name}"] = forms.CharField(
            label=search_config.simple_query_label,
            required=False,
            max_length=100,
            help_text=mark_safe(
                f'<small class="form-text text-muted">{search_config.simple_query_help_text}</small>'
            ),
        )

        if search_config.show_and_or_field:
            self.fields[f"and_or_field_{search_config.conf_name}"] = forms.ChoiceField(
                label=_("And or Or Search"),
                choices=[("and", _("AND search")), ("or", _("OR search"))],
                required=False,
            )

        if search_config.search_has_compact_result:
            self.fields[
                f"compact_view_{search_config.conf_name}_simple"
            ] = self.get_compact_view_field(search_config)

    def init_combined_simple_search_fields(self, master_config):
        """Create form fields for the combined simple search tab (single field shared across all configs)."""
        self.fields['search_term_combined_simple'] = forms.CharField(
            label=master_config.simple_query_label,
            required=False,
            max_length=100,
            help_text=mark_safe(
                f'<small class="form-text text-muted">{master_config.simple_query_help_text}</small>'
            ),
        )
        if master_config.show_and_or_field:
            self.fields['and_or_field_combined_simple'] = forms.ChoiceField(
                label=_("And or Or Search"),
                choices=[("and", _("AND search")), ("or", _("OR search"))],
                required=False,
            )
        if master_config.search_has_compact_result:
            self.fields['compact_view_combined_simple'] = self.get_compact_view_field(master_config)

    @staticmethod
    def get_simple_search_layout_fields(search_config):
        """Create and return layout fields for the simple search fields."""

        fields = [Field(f"search_term_{search_config.conf_name}", wrapper_class="col-md-12")]
        if search_config.show_and_or_field:
            fields.append(Field(f"and_or_field_{search_config.conf_name}", wrapper_class="col-md-4"))
        return fields

    @staticmethod
    def get_combined_search_button(master_config=None):
        """Create and return right-aligned search button for the combined simple search tab."""
        elements = []

        if master_config and master_config.search_has_compact_result:
            elements.append(Field('compact_view_combined_simple', wrapper_class="mb-0 align-self-center"))

        elements.append(NdrCoreFormSubmit('search_button_combined_simple', _("Search")))
        elements.append(NdrCoreClearButton(_("Clear")))

        return Div(*elements, css_class="d-flex justify-content-end align-items-center gap-2 mt-2")

    @staticmethod
    def get_search_button(search_config, simple=False):
        """Create and return right-aligned search button."""
        search_button_field_name = f"search_button_{search_config.conf_name}"
        if simple:
            search_button_field_name += "_simple"

        elements = []

        if search_config.search_has_compact_result:
            field_name = f"compact_view_{search_config.conf_name}"
            if simple:
                field_name += "_simple"
            elements.append(Field(field_name, wrapper_class="mb-0 align-self-center"))

        elements.append(NdrCoreFormSubmit(search_button_field_name, _("Search")))
        elements.append(NdrCoreClearButton(_("Clear")))

        return Div(*elements, css_class="d-flex justify-content-end align-items-center gap-2 mt-2")

    @property
    def helper(self):
        """Creates and returns the form helper class with the layout-ed form fields."""

        helper = FormHelper()
        helper.form_method = "GET"
        layout = helper.layout = Layout()

        # There can be multiple search configurations for one page. Each of them gets its own tab.
        tabs = TabHolder(css_id="id_tabs")

        # If combined simple search is enabled, prepend the unified tab.
        if self.combined_simple_config:
            master = self.combined_simple_config
            tab_combined = Tab(
                master.simple_search_tab_title,
                css_id='combined_simple',
            )
            tab_combined.append(Div(
                Field('search_term_combined_simple', wrapper_class='col-md-12'),
                css_class='row g-2 mt-2',
            ))
            if master.show_and_or_field:
                tab_combined.append(Div(
                    Field('and_or_field_combined_simple', wrapper_class='col-md-4'),
                    css_class='row g-2 mt-2',
                ))
            tab_combined.append(self.get_combined_search_button(master))
            tabs.append(tab_combined)

        # For each search configuration, create a tab and add the form fields to it.
        for search_config in self.search_configs:
            # Each search configuration can have a simple search tab (suppressed in combined mode).
            tab_simple = None
            if search_config.has_simple_search and not self.combined_simple_config:
                tab_simple = Tab(
                    search_config.simple_search_tab_title,
                    css_id=f"{search_config.conf_name}_simple",
                )
                fields = self.get_simple_search_layout_fields(search_config)
                tab_simple.append(Div(fields[0], css_class="row g-2 mt-2"))
                if len(fields) > 1:
                    tab_simple.append(Div(*fields[1:], css_class="row g-2 mt-2"))

                tab_simple.append(self.get_search_button(search_config, simple=True))
                if search_config.simple_search_first:
                    tabs.append(tab_simple)

            # This id the tab of the advanced search.
            tab = Tab(search_config.conf_label, css_id=search_config.conf_name)

            # The form fields are grouped by row and column. The row is the outer loop.
            max_row = search_config.search_form_fields.all().aggregate(Max("field_row"))
            field_range = max_row["field_row__max"]
            if field_range is None:
                field_range = 0

            for row in range(field_range):
                row += 1  # The row starts with 1, not 0.
                form_row = Div(css_class="row g-2 mt-2")
                # The column is the inner loop.
                for column in search_config.search_form_fields.filter(field_row=row).order_by("field_column"):
                    # Type is INFO_TEXT, so we create a div with the text.
                    if column.search_field.field_type == column.search_field.FieldType.INFO_TEXT:
                        try:
                            info_text_translation = NdrCoreTranslation.objects.get(
                                object_id=column.search_field.field_name,
                                language=get_language(),
                                field_name="text_choices",
                                table_name="ndrcoresearchfield",
                            )
                            info_text = info_text_translation.translation
                        except NdrCoreTranslation.DoesNotExist:
                            # text_choices is the canonical store; fall back to list_choices
                            # for fields saved before this fix.
                            raw = column.search_field.text_choices or column.search_field.list_choices
                            info_text = "" if not raw or raw.strip() in ("", "[]", "null") else raw

                        if column.search_field.show_label:
                            title_html = (
                                f'<i class="fa-regular fa-circle-info"></i>&nbsp;'
                                f"<strong>{column.search_field.field_label}</strong><br/>"
                            )
                        else:
                            title_html = ''
                        form_field = Div(
                            HTML(
                                mark_safe(
                                    f'<div class="alert alert-info small" role="alert">'
                                    f"{title_html}"
                                    f"{info_text}"
                                    f"</div>"
                                )
                            ),
                            css_class=f"col-md-{column.field_size}",
                        )
                    else:
                        # If the field is a list and set to CHOOSE, we create a select field.
                        if f"{search_config.conf_name}_{column.search_field.field_name}_condition" in self.fields:
                            form_field = Div(
                                Div(
                                    Field(
                                        f"{search_config.conf_name}_{column.search_field.field_name}",
                                        wrapper_class="col-9 m-0 pr-0",
                                    ),
                                    Field(
                                        f"{search_config.conf_name}_{column.search_field.field_name}_condition",
                                        css_class="",
                                        wrapper_class="col-3 m-0 pl-0",
                                    ),
                                    css_class="row"
                                ),
                                css_class=f"col-md-{column.field_size}",
                            )
                        # If the field has an operator dropdown (comparison_operator set to CHOOSE)
                        elif f"{search_config.conf_name}_{column.search_field.field_name}_operator" in self.fields:
                            form_field = Div(
                                Div(
                                    Field(
                                        f"{search_config.conf_name}_{column.search_field.field_name}",
                                        wrapper_class="col-9 m-0 pr-0",
                                    ),
                                    Field(
                                        f"{search_config.conf_name}_{column.search_field.field_name}_operator",
                                        css_class="",
                                        wrapper_class="col-3 m-0 pl-0",
                                    ),
                                    css_class="row"
                                ),
                                css_class=f"col-md-{column.field_size}",
                            )
                        # Otherwise, we create a normal field.
                        else:
                            form_field = Field(
                                f"{search_config.conf_name}_{column.search_field.field_name}",
                                # placeholder=column.search_field.translated_field_label(),
                                wrapper_class=f"col-md-{column.field_size}",
                            )

                    form_row.append(form_field)

                tab.append(form_row)

            # Only add the tab if there are fields in it.
            if search_config.search_form_fields.all().count() > 0:
                tab.append(self.get_search_button(search_config))
                tabs.append(tab)

            if search_config.has_simple_search and not search_config.simple_search_first and not self.combined_simple_config:
                tabs.append(tab_simple)

        if len(tabs) == 1:
            # "Only one tab, removing tab holder."
            layout.append(tabs[0])
        else:
            layout.append(tabs)

        helper.form_show_labels = True

        return helper
