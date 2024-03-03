"""Contains forms used in the NDRCore admin interface to edit translations."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import (
    NdrCorePage,
    NdrCoreTranslation,
    NdrCoreSearchField,
    NdrCoreValue,
    NdrCoreSearchConfiguration,
    NdrCoreUIElement,
    NdrCoreImage,
    NdrCoreResultField,
)


class TranslateForm(forms.Form):
    """Base form to translate values."""

    lang = "en"
    table_name = None
    translatable_fields = []
    items = []

    def __init__(self, *args, **kwargs):
        if "lang" in kwargs:
            self.lang = kwargs.pop("lang")

        super().__init__(*args, **kwargs)

    def init_form(self):
        """Initializes the form."""
        initial_values = {}
        for item in self.items:
            for field in self.translatable_fields:
                values = {}
                if isinstance(field, dict):
                    values = field
                    field = values["field"]

                if "condition" in values:
                    if (
                        item.__getattribute__(values["condition"]["field"])
                        not in values["condition"]["values"]
                    ):
                        continue

                self.fields[f"{field}_{item.pk}"] = forms.CharField(
                    label=f"Translate: '{field}' for '{item.__getattribute__(field)}'",
                    required=False,
                    max_length=1000,
                    help_text="",
                )
                if "widget" in values and values["widget"] == "textarea":
                    self.fields[f"{field}_{item.pk}"].widget = forms.Textarea(
                        attrs={"rows": 3}
                    )

                initial_values[f"{field}_{item.pk}"] = self.get_initial_value(
                    field, str(item.pk)
                )

        self.initial = initial_values

    def do_helper(self):
        """Creates and returns the form helper property."""

        helper = FormHelper()
        helper.form_method = "POST"
        layout = helper.layout = Layout()

        for item in self.items:
            cols = []
            for field in self.translatable_fields:
                values = {}
                if isinstance(field, dict):
                    values = field
                    field = values["field"]

                if "condition" in values:
                    if (
                        item.__getattribute__(values["condition"]["field"])
                        not in values["condition"]["values"]
                    ):
                        continue

                cols.append(
                    Column(
                        f"{field}_{item.pk}",
                        css_class=f"form-group col-{int(12/len(self.translatable_fields))}",
                    ),
                )

            form_row = Row(*cols, css_class="form-row")
            layout.append(form_row)

        layout.append(get_form_buttons("Save Translations"))

        return helper

    def get_initial_value(self, field_name, object_id):
        """Returns the initial value of the field."""
        try:
            translation_obj = NdrCoreTranslation.objects.get(
                language=self.lang,
                table_name=self.table_name.lower(),
                field_name=field_name,
                object_id=object_id,
            )
            return translation_obj.translation
        except NdrCoreTranslation.DoesNotExist:
            return ""

    def save_translations(self):
        """Saves the translations to the database."""
        self.is_valid()

        for item in self.items:
            for field in self.translatable_fields:
                values = {}
                if isinstance(field, dict):
                    values = field
                    field = values["field"]

                if "condition" in values:
                    if (
                        item.__getattribute__(values["condition"]["field"])
                        not in values["condition"]["values"]
                    ):
                        continue

                self.save_translation(
                    str(item.pk), field, self.cleaned_data[f"{field}_{item.pk}"]
                )

    def save_translation(self, object_id, field_name, translation):
        """Saves the translation to the database."""
        i18n_object = NdrCoreTranslation.objects.get_or_create(
            language=self.lang,
            table_name=self.table_name.lower(),
            field_name=field_name,
            object_id=object_id,
        )
        i18n_object[0].translation = translation
        i18n_object[0].save()


class TranslatePageForm(TranslateForm):
    """Form to translate page values"""

    items = NdrCorePage.objects.all()
    translatable_fields = ["name", "label"]
    table_name = "NdrCorePage"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_form()

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        return self.do_helper()


class TranslateFieldForm(TranslateForm):
    """Form to translate form field values"""

    items = NdrCoreSearchField.objects.all()
    translatable_fields = [
        "field_label",
        "help_text",
        {
            "field": "list_choices",
            "widget": "textarea",
            "condition": {
                "field": "field_type",
                "values": [NdrCoreSearchField.FieldType.INFO_TEXT],
            },
        },
    ]
    table_name = "NdrCoreSearchField"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_form()

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        return self.do_helper()


class TranslateSettingsForm(TranslateForm):
    """Form to translate settings values."""

    items = NdrCoreValue.objects.filter(
        value_type__in=[NdrCoreValue.ValueType.STRING, NdrCoreValue.ValueType.URL],
        is_translatable=True,
    )
    translatable_fields = ["value_value"]
    table_name = "NdrCoreValue"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_form()

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        return self.do_helper()


class TranslateFormForm(TranslateForm):
    """Form to translate settings values."""

    items = NdrCoreSearchConfiguration.objects.all()
    translatable_fields = ["conf_label"]
    table_name = "NdrCoreSearchConfiguration"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_form()

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        return self.do_helper()


class TranslateResultForm(TranslateForm):
    """Form to translate settings values."""

    items = NdrCoreResultField.objects.all()
    translatable_fields = [{"field": "rich_expression", "widget": "textarea"}]
    table_name = "NdrCoreResultField"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_form()

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        return self.do_helper()


class TranslateUIElementsForm(TranslateForm):
    """Form to translate settings values."""

    items = NdrCoreUIElement.objects.all()
    translatable_fields = ["conf_label"]
    table_name = "NdrCoreUIElement"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_form()

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        return self.do_helper()


class TranslateImagesForm(TranslateForm):
    """Form to translate settings values."""

    items = NdrCoreImage.objects.filter(image_group="figures")
    translatable_fields = ["title", "caption"]
    table_name = "NdrCoreImage"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_form()

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        return self.do_helper()
