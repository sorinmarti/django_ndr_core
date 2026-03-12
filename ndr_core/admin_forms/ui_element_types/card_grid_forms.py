"""Forms for Card Grid UI Element type."""
from crispy_forms.layout import Row, Column, HTML
from django import forms
from django.forms import inlineformset_factory

from ndr_core.admin_forms.admin_forms import get_form_buttons
from ndr_core.models import NdrCoreUIElement, NdrCoreUiElementItem
from .base_forms import BaseUIElementForm


class CardGridItemForm(forms.ModelForm):
    """Form for a single card slot in the grid."""

    card_element = forms.ModelChoiceField(
        queryset=None,  # Set in __init__
        required=False,
        label='Card',
        help_text='Select a Card UI element to include in the grid',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = NdrCoreUiElementItem
        fields = []  # We handle fields manually

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['card_element'].queryset = NdrCoreUIElement.objects.filter(
            type=NdrCoreUIElement.UIElementType.CARD
        ).order_by('name')

        # Populate initial value if editing
        if self.instance and self.instance.pk and self.instance.object_id:
            try:
                self.fields['card_element'].initial = NdrCoreUIElement.objects.get(
                    name=self.instance.object_id
                )
            except NdrCoreUIElement.DoesNotExist:
                pass

    def save(self, commit=True):
        """Save the card grid item, storing the referenced card's name in object_id."""
        instance = super().save(commit=False)
        card_element = self.cleaned_data.get('card_element')
        instance.object_id = card_element.name if card_element else ''
        # ORDER field is added by can_order=True in the formset
        instance.order_idx = self.cleaned_data.get('ORDER') or 0
        if commit:
            instance.save()
        return instance


CardGridItemFormSet = inlineformset_factory(
    NdrCoreUIElement,
    NdrCoreUiElementItem,
    form=CardGridItemForm,
    extra=3,
    max_num=20,
    can_delete=True,
    can_order=True,
)


class CardGridForm(BaseUIElementForm):
    """Form for Card Grid UI Element - displays existing cards in a responsive grid."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, ui_element_type='card_grid', **kwargs)

    @property
    def helper(self):
        helper = self.get_base_helper()
        helper.form_tag = False  # The template wraps everything in its own <form> tag

        layout = helper.layout
        self.add_info_section(
            layout,
            'Card Grid UI Element',
            'A Card Grid displays a collection of existing Card elements in a responsive grid layout. '
            'Create your cards first, then select them here to arrange them in a grid.'
        )
        self.add_field_row(layout, 'name', 'label', col_class='col-md-6')
        return helper


class CardGridCreateForm(CardGridForm):
    """Form to create a new Card Grid UI Element."""
    pass


class CardGridEditForm(CardGridForm):
    """Form to edit an existing Card Grid UI Element."""

    def __init__(self, *args, **kwargs):
        self._original_name = kwargs['instance'].name if 'instance' in kwargs else None
        super().__init__(*args, **kwargs)
        self.fields['name'].help_text = 'Unique slug/identifier. Can be changed - renaming will preserve all settings.'

    def save(self, commit=True):
        """Save with special handling for name changes (PK changes)."""
        name_changed = self._original_name and self._original_name != self.cleaned_data.get('name')

        if name_changed and commit:
            old_instance = NdrCoreUIElement.objects.get(name=self._original_name)
            new_instance = super().save(commit=True)
            new_instance._old_instance_to_delete = old_instance
            return new_instance
        else:
            return super().save(commit=commit)