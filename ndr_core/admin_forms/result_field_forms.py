"""Contains forms used in the NDRCore admin interface for the creation or edit of result fields."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django import forms

from ndr_core.admin_forms.admin_forms import get_form_buttons, get_info_box
from ndr_core.admin_forms.widgets import TabChildrenWidget
from ndr_core.models import NdrCoreResultField


class ResultFieldForm(forms.ModelForm):
    """Form to create or edit a search field form. """

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreResultField
        fields = ['label', 'rich_expression', 'field_classes', 'border_label']

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = FormHelper()
        layout = helper.layout = Layout()
        helper.form_method = "POST"

        form_row = Row(
            Column('label', css_class='form-group col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('rich_expression', css_class='form-group col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column('field_classes', css_class='form-group col-6'),
            Column('border_label', css_class='form-group col-6'),
            css_class='row g-2'
        )
        layout.append(form_row)

        form_row = Row(
            Column(
                get_info_box('Access your variables in the following form', 'xxx_info'),
                css_class='form-group col-12'
            ),
            css_class='row g-2'
        )
        layout.append(form_row)

        return helper


class ResultFieldCreateForm(ResultFieldForm):
    """Form to create a search field form. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Result Field', include_save_and_continue=True))
        return helper


class ResultFieldEditForm(ResultFieldForm):
    """Form to edit a search field form. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save Result Field', include_save_and_continue=True))
        return helper


class TabFieldForm(forms.ModelForm):
    """Simplified form to create or edit a tab container field. """

    tab_children_text = forms.CharField(
        widget=TabChildrenWidget(),
        required=False,
        label='Tab Configuration',
        help_text='Configure the tabs that will be displayed in this container.'
    )

    class Meta:
        """Configure the model form. Provide model class and form fields."""
        model = NdrCoreResultField
        fields = ['label']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate tab_children_text if editing existing object
        if self.instance and self.instance.pk and self.instance.tab_children:
            import json
            self.fields['tab_children_text'].initial = json.dumps(self.instance.tab_children, indent=2)

    def clean_tab_children_text(self):
        """Validate and parse the JSON input."""
        import json
        text = self.cleaned_data.get('tab_children_text', '').strip()
        if not text:
            return None
        try:
            data = json.loads(text)
            if not isinstance(data, list):
                raise forms.ValidationError("Tab children must be a JSON array")
            # Validate structure
            for item in data:
                if not isinstance(item, dict):
                    raise forms.ValidationError("Each tab must be a JSON object")
                if 'tab_label' not in item or 'result_field_id' not in item:
                    raise forms.ValidationError("Each tab must have 'tab_label' and 'result_field_id'")
            return data
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Invalid JSON: {str(e)}")

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Save the parsed JSON to the tab_children field
        instance.tab_children = self.cleaned_data.get('tab_children_text')
        instance.is_tab_container = True
        if commit:
            instance.save()
        return instance

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        from crispy_forms.layout import HTML, Div

        helper = FormHelper()
        layout = helper.layout = Layout()
        helper.form_method = "POST"

        # Info box
        layout.append(Div(
            HTML('<div class="alert alert-info">'
                 '<strong><i class="fa-regular fa-circle-info"></i> Tab Container Field:</strong> '
                 'This field will display multiple result fields as tabs. Each tab shows one result field. '
                 'Add tabs below and select which result field should be displayed in each tab.'
                 '</div>'),
            css_class='mb-3'
        ))

        # Label field
        form_row = Row(
            Column('label', css_class='form-group col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        # Tab configuration widget
        form_row = Row(
            Column('tab_children_text', css_class='form-group col-12'),
            css_class='row g-2'
        )
        layout.append(form_row)

        return helper


class TabFieldCreateForm(TabFieldForm):
    """Form to create a tab container field. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Create Tab Field', include_save_and_continue=True))
        return helper


class TabFieldEditForm(TabFieldForm):
    """Form to edit a tab container field. """

    @property
    def helper(self):
        """Creates and returns the form helper property."""
        helper = super().helper
        helper.layout.append(get_form_buttons('Save Tab Field', include_save_and_continue=True))
        return helper
