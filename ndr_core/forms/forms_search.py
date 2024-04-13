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
    FilteredListWidget
)


class AdvancedSearchForm(_NdrCoreForm):
    """Form class for the search.
    Needs a search config and then creates and configures the form from it."""

    search_configs = None

    def __init__(self, *args, **kwargs):
        """Initializes all needed form fields for the configured search based on
        the page's search configuration."""

        if "ndr_page" in kwargs:
            self.ndr_page = kwargs.pop("ndr_page")

        if self.ndr_page is not None:
            self.search_configs = self.ndr_page.search_configs.all()
        elif "search_config" in kwargs:
            self.search_configs = [kwargs.pop("search_config")]
        else:
            raise AttributeError("No Search Config Found")

        super().__init__(*args, **kwargs)

        self.query_dict = {}
        if len(args) > 0:
            self.query_dict = self.query_dict_to_dict(args[0])

        # Search Form is composed of different search configurations. Each of them has its own tab.
        # A search configuration may have a simple search tab as well.
        for search_config in self.search_configs:
            # If the search configuration has a simple search tab, add the fields to the form.
            if search_config.has_simple_search:
                self.init_simple_search_fields(search_config)

            # If the search configuration has an advanced search tab, add the fields to the form.
            if search_config.search_has_compact_result:
                self.fields[
                    f"compact_view_{search_config.conf_name}"
                ] = self.get_compact_view_field()

            # Add the fields of the search configuration to the form.
            for field in search_config.search_form_fields.all():
                search_field = field.search_field
                form_field = None
                condition_form_field = None
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
                # Number field
                if search_field.field_type == search_field.FieldType.NUMBER:
                    form_field = forms.IntegerField(
                        label=search_field.field_label,
                        required=search_field.field_required,
                        help_text=help_text,
                        initial=search_field.get_initial_value(),
                    )
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
                # Date range field
                if search_field.field_type == search_field.FieldType.DATE_RANGE:
                    # search_field.lower_value is in the form YYYY-MM-DD. Convert it to DD.MM.YYYY
                    lower_value = search_field.lower_value
                    if lower_value is not None:
                        lower_value = (
                            f"{lower_value[8:10]}.{lower_value[5:7]}.{lower_value[0:4]}"
                        )
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
                                "minYear": int(lower_value[6:10]),
                                "maxYear": int(upper_value[6:10]),
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
                                                                 help_text="<small>AND: all.<br/>OR: at least one.</small>")

                # Add the field to the form if it was created.
                if form_field is not None:
                    self.fields[
                        f"{search_config.conf_name}_{search_field.field_name}"
                    ] = form_field
                    # Add the condition field to the form if it was created.
                    if condition_form_field is not None:
                        self.fields[
                            f"{search_config.conf_name}_{search_field.field_name}_condition"
                        ] = condition_form_field

    @staticmethod
    def get_compact_view_field():
        """Returns the compact view field for the given search configuration."""
        return forms.BooleanField(
            required=False,
            widget=BootstrapSwitchWidget(attrs={"label": _("Compact Result View")}),
            label="",
        )

    def init_simple_search_fields(self, search_config):
        """Create form fields for simple search."""

        self.fields[f"search_term_{search_config.conf_name}"] = forms.CharField(
            label=search_config.simple_query_label,
            required=False,
            max_length=100,
            help_text=search_config.simple_query_help_text,
        )

        self.fields[f"and_or_field_{search_config.conf_name}"] = forms.ChoiceField(
            label=_("And or Or Search"),
            choices=[("and", _("AND search")), ("or", _("OR search"))],
            required=False,
        )

        if search_config.search_has_compact_result:
            self.fields[
                f"compact_view_{search_config.conf_name}_simple"
            ] = self.get_compact_view_field()

    @staticmethod
    def get_simple_search_layout_fields(search_config):
        """Create and return layout fields for the simple search fields."""

        search_field = Field(
            f"search_term_{search_config.conf_name}", wrapper_class="col-md-12"
        )
        type_field = Field(
            f"and_or_field_{search_config.conf_name}", wrapper_class="col-md-4"
        )

        return search_field, type_field

    @staticmethod
    def get_search_button(search_config, simple=False):
        """Create and return right aligned search button."""
        search_button_field_name = f"search_button_{search_config.conf_name}"
        if simple:
            search_button_field_name += "_simple"

        compact_field = None
        if search_config.search_has_compact_result:
            field_name = f"compact_view_{search_config.conf_name}"
            if simple:
                field_name += "_simple"
            compact_field = Field(field_name, wrapper_class="col-md-12")

        div = Div(
            Div(css_class="col-md-5"),
            Div(Div(compact_field, css_class="text-right"), css_class="col-md-4"),
            Div(
                Div(
                    NdrCoreFormSubmit(search_button_field_name, _("Search")),
                    css_class="text-right",
                ),
                css_class="col-md-3",
            ),
            css_class="form-row",
        )
        return div

    @property
    def helper(self):
        """Creates and returns the form helper class with the layout-ed form fields."""

        helper = FormHelper()
        helper.form_method = "GET"
        layout = helper.layout = Layout()

        # There can be multiple search configurations for one page. Each of them gets its own tab.
        tabs = TabHolder(css_id="id_tabs")

        # For each search configuration, create a tab and add the form fields to it.
        for search_config in self.search_configs:
            # Each search configuration can have a simple search tab.
            tab_simple = None
            if search_config.has_simple_search:
                tab_simple = Tab(
                    search_config.simple_search_tab_title,
                    css_id=f"{search_config.conf_name}_simple",
                )
                fields = self.get_simple_search_layout_fields(search_config)
                tab_simple.append(Div(fields[0], css_class="form-row"))
                tab_simple.append(Div(*fields[1:], css_class="form-row"))

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
                form_row = Div(css_class="form-row")
                # The column is the inner loop.
                for column in search_config.search_form_fields.filter(field_row=row).order_by("field_column"):
                    # Type is INFO_TEXT, so we create a div with the text.
                    if column.search_field.field_type == column.search_field.FieldType.INFO_TEXT:
                        try:
                            info_text_translation = NdrCoreTranslation.objects.get(
                                object_id=column.search_field.field_name,
                                language=get_language(),
                                field_name="list_choices",
                                table_name="ndrcoresearchfield",
                            )
                            info_text = info_text_translation.translation
                        except NdrCoreTranslation.DoesNotExist:
                            info_text = column.search_field.list_choices

                        form_field = Div(
                            HTML(
                                mark_safe(
                                    f'<div class="alert alert-info small" role="alert">'
                                    f'<i class="fa-regular fa-circle-info"></i>&nbsp;'
                                    f"<strong>{column.search_field.field_label}</strong><br/>"
                                    f"{info_text}"
                                    f"</div>"
                                )
                            ),
                            css_class=f"col-md-{column.field_size}",
                        )
                    else:
                        # If the field is a list and set to CHOOSE, we create a select field.
                        if f"{search_config.conf_name}_{column.search_field.field_name}_condition" in self.fields:
                            print("Adding condition field for ", column.search_field.field_name)
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

            if (
                search_config.has_simple_search
                and not search_config.simple_search_first
            ):
                tabs.append(tab_simple)

        layout.append(tabs)

        helper.form_show_labels = True

        return helper
