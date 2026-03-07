"""Template tags for the ndr_core app."""
import json
import re
import uuid
from datetime import datetime, timedelta

from django import template
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils import timezone
from ndr_core.ndr_templatetags.template_string import TemplateString

register = template.Library()

@register.tag(name="render_single")
def render_single_tag(parser, token):
    """Renders a single result without header/footer wrapper.
    Usage: {% render_single result search_config %}"""
    token_list = token.split_contents()
    return RenderSingleNode(token_list[1], token_list[2])

class RenderSingleNode(template.Node):
    """Renders a single result using the full detail card without the header/footer wrapper."""

    def __init__(self, result, search_config):
        self.result = template.Variable(result)
        self.search_config = template.Variable(search_config)

    def render(self, context):
        """Renders the single result detail view."""
        result_object = self.result.resolve(context)

        # Get first result from the result object
        if not result_object.results or len(result_object.results) == 0:
            return ""

        result_data = result_object.results[0]

        # Reuse the existing grid creation logic
        card_content = self.create_grid(context, result_data["data"], "normal")

        # Use simplified template without header/footer
        # Get search_term from parent context if available
        search_term = context.get('search_term', '')

        card_context = {
            "card_content": card_content,
            "search_term": search_term,
        }
        card_template = "ndr_core/result_renderers/single_detail_template.html"

        card_template_str = get_template(card_template).render(card_context)
        return mark_safe(card_template_str)

    def create_grid(self, context, data, compact_view):
        """Creates a CSS Grid of result fields - copied from RenderResultNode."""
        result_card_fields = self.search_config.resolve(
            context
        ).result_card_fields.filter(result_card_group=compact_view).order_by('field_row', 'field_column')

        if not result_card_fields.exists():
            return ""

        return RenderResultNode.create_simple_grid(result_card_fields, data)

    @staticmethod
    def create_field(field_config, data):
        """Creates a result field with CSS Grid positioning - copied from RenderResultNode."""
        field_template = "ndr_core/result_renderers/elements/result_field.html"
        result_field = field_config.result_field

        template_string = TemplateString(
            result_field.rich_expression, data, show_errors=True
        )
        field_content = template_string.get_formatted_string()
        field_content = template_string.sanitize_html(field_content)

        field_context = {
            "field_row": field_config.field_row,
            "field_column": field_config.field_column,
            "field_column_span": field_config.field_column_span,
            "field_row_span": field_config.field_row_span,
            "classes": result_field.field_classes,
            "field_content": field_content,
            "border_label": result_field.border_label,
        }
        field_template_str = get_template(field_template).render(field_context)
        return mark_safe(field_template_str)


@register.tag(name="render_data_list")
def render_data_list_tag(parser, token):
    """Renders a result object. The token is expected to be in the following format:
    {% render_result result search_config result_card_group %}"""
    token_list = token.split_contents()
    return RenderDataListNode(token_list[1], token_list[2])

class RenderDataListNode(template.Node):
    """Renders a result object."""

    def __init__(self, result, search_config):
        self.result = template.Variable(result)
        self.search_config = template.Variable(search_config)

    def create_entry(self, context, result):
        """Creates a result card using the compact result card configuration."""

        conf = self.search_config.resolve(context)

        # Use the compact result card configuration to render the list item
        card_content = self.create_grid(context, result["data"], "compact")

        # Get the result ID for the detail page link
        result_id = result['data'].get(conf.search_id_field, '')
        search_term = context.get('search_term', '')

        # If no compact configuration exists, fall back to simple id/label display
        if not card_content:
            card_content = {"id": result_id,
                           "label": result['data'][conf.simple_query_main_field],
                           "search_term": search_term}

        card_context = {
            "result": result,
            "card_content": card_content,
            "result_id": result_id,
            "search_term": search_term,
        }
        card_template = "ndr_core/result_renderers/data_list_template.html"

        card_template_str = get_template(card_template).render(card_context)
        return mark_safe(card_template_str)

    def create_grid(self, context, data, compact_view):
        """Creates a CSS Grid of result fields using the compact configuration."""
        result_card_fields = self.search_config.resolve(
            context
        ).result_card_fields.filter(result_card_group=compact_view).order_by('field_row', 'field_column')

        if not result_card_fields.exists():
            return ""

        return RenderResultNode.create_simple_grid(result_card_fields, data)

    @staticmethod
    def create_field(field_config, data):
        """Creates a result field with CSS Grid positioning."""
        field_template = "ndr_core/result_renderers/elements/result_field.html"
        result_field = field_config.result_field

        template_string = TemplateString(
            result_field.rich_expression, data, show_errors=True
        )
        field_content = template_string.get_formatted_string()
        field_content = template_string.sanitize_html(field_content)

        field_context = {
            "field_row": field_config.field_row,
            "field_column": field_config.field_column,
            "field_column_span": field_config.field_column_span,
            "field_row_span": field_config.field_row_span,
            "classes": result_field.field_classes,
            "field_content": field_content,
            "border_label": result_field.border_label,
        }
        field_template_str = get_template(field_template).render(field_context)
        return mark_safe(field_template_str)

    def render(self, context):
        """Renders a result object."""
        result_object = self.result.resolve(context)
        html_string = ""
        for result in result_object.results:
                html_string += self.create_entry(context, result)

        return mark_safe(html_string)


@register.tag(name="render_result")
def render_result_tag(parser, token):
    """Renders a result object. The token is expected to be in the following format:
    {% render_result result search_config result_card_group %}"""
    token_list = token.split_contents()
    return RenderResultNode(token_list[1], token_list[2])


class RenderResultNode(template.Node):
    """Renders a result object."""

    def __init__(self, result, search_config):
        self.result = template.Variable(result)
        self.search_config = template.Variable(search_config)

    def create_card(self, context, result, compact_view):
        """Creates a result card."""

        card_context = {
            "result": result,
            "card_content": self.create_grid(context, result["data"], compact_view),
            "citation": self.create_citation(context, result["data"]),
        }
        card_template = "ndr_core/result_renderers/configured_fields_template.html"

        card_template_str = get_template(card_template).render(card_context)
        return mark_safe(card_template_str)

    def create_citation(self, context, result):
        """Creates a citation."""
        exp = self.search_config.resolve(context).citation_expression
        if exp is None or exp == "":
            return ""  # Return empty string if no citation expression

        template_string = TemplateString(exp, result, show_errors=False)
        citation = template_string.get_formatted_string()
        citation = template_string.sanitize_html(citation)
        return mark_safe(citation)

    def create_grid(self, context, data, compact_view):
        """Creates a CSS Grid of result fields, with tab support."""
        result_card_fields = self.search_config.resolve(
            context
        ).result_card_fields.filter(result_card_group=compact_view).order_by('field_row', 'field_column')

        if not result_card_fields.exists():
            return ""

        return self.create_simple_grid(result_card_fields, data)

    @staticmethod
    def create_simple_grid(field_configs, data):
        """Creates a CSS Grid container for result fields."""
        grid_html = '<div class="result-grid">'

        for field_config in field_configs:
            field_html = RenderResultNode.create_field(field_config, data)
            grid_html += field_html

        grid_html += '</div>'
        return mark_safe(grid_html)

    @staticmethod
    def render_tab_container(result_field, data):
        """Renders a tab container with child result fields as tabs."""
        from ndr_core.models import NdrCoreResultField

        if not result_field.tab_children:
            return "<div class='alert alert-warning'>Tab container has no children configured</div>"

        # Generate unique ID for this tab container
        tab_id = f"tab-container-{uuid.uuid4().hex[:8]}"

        # Sort tabs by tab_order (default to 999 if not set)
        sorted_tabs = sorted(
            result_field.tab_children,
            key=lambda x: x.get('tab_order', 999)
        )

        # Build tab navigation
        tab_html = '<div class="tab-container-field">'
        tab_html += '<ul class="nav nav-tabs" role="tablist">'

        for idx, tab_config in enumerate(sorted_tabs):
            tab_label = tab_config.get('tab_label', f'Tab {idx + 1}')
            active = 'active' if idx == 0 else ''
            tab_html += f'''
                <li class="nav-item">
                    <a class="nav-link {active}" data-bs-toggle="tab"
                       href="#{tab_id}-{idx}" role="tab">{tab_label}</a>
                </li>
            '''

        tab_html += '</ul>'
        tab_html += '<div class="tab-content">'

        # Build tab panes with child field content
        for idx, tab_config in enumerate(sorted_tabs):
            active = 'show active' if idx == 0 else ''
            tab_html += f'<div class="tab-pane fade {active}" id="{tab_id}-{idx}" role="tabpanel">'

            # Get the child result field
            child_field_id = tab_config.get('result_field_id')
            if child_field_id:
                try:
                    child_field = NdrCoreResultField.objects.get(pk=child_field_id)

                    # Render the child field's content
                    template_string = TemplateString(
                        child_field.rich_expression, data, show_errors=True
                    )
                    child_content = template_string.get_formatted_string()
                    child_content = template_string.sanitize_html(child_content)

                    tab_html += f'<div class="tab-pane-content">{child_content}</div>'
                except NdrCoreResultField.DoesNotExist:
                    tab_html += f'<div class="alert alert-danger">Result field {child_field_id} not found</div>'
            else:
                tab_html += '<div class="alert alert-warning">No result field configured for this tab</div>'

            tab_html += '</div>'

        tab_html += '</div></div>'

        return mark_safe(tab_html)

    @staticmethod
    def create_field(field_config, data):
        """Creates a result field with CSS Grid positioning."""
        field_template = "ndr_core/result_renderers/elements/result_field.html"
        result_field = field_config.result_field

        # Check if this is a tab container field
        if result_field.is_tab_container and result_field.tab_children:
            field_content = RenderResultNode.render_tab_container(result_field, data)
        else:
            template_string = TemplateString(
                result_field.rich_expression, data, show_errors=True
            )
            field_content = template_string.get_formatted_string()
            field_content = template_string.sanitize_html(field_content)

        field_context = {
            # Remove old Bootstrap size, add CSS Grid properties
            "field_row": field_config.field_row,
            "field_column": field_config.field_column,
            "field_column_span": field_config.field_column_span,
            "field_row_span": field_config.field_row_span,
            "classes": result_field.field_classes,
            "field_content": field_content,
            "border_label": result_field.border_label,
        }
        field_template_str = get_template(field_template).render(field_context)
        return mark_safe(field_template_str)

    def render(self, context):
        """Renders a result object."""
        result_object = self.result.resolve(context)
        conf = self.search_config.resolve(context)

        compact_view = "normal"
        if (
                result_object.request.GET.get(f"compact_view_{conf.conf_name}_simple", "off") == "on"
                or result_object.request.GET.get(f"compact_view_{conf.conf_name}", "off") == "on"
        ):
            compact_view = "compact"

        num_result_fields = (
            self.search_config.resolve(context).result_card_fields.all().count()
        )

        html_string = ""
        for result in result_object.results:
            if num_result_fields > 0:
                html_string += self.create_card(context, result, compact_view)
            else:
                # No result card fields configured, so we render the result as pretty json
                card_context = {"result": result}
                card_template = "ndr_core/result_renderers/default_template.html"
                html_string += get_template(card_template).render(card_context)

        return mark_safe(html_string)


@register.filter
def pretty_json(value):
    """Pretty prints a json string."""
    pretty_json_str = json.dumps(value, indent=4)
    pretty_json_str = pretty_json_str.replace("\n", "<br>").replace(" ", "&nbsp;")
    pretty_json_str = re.sub(
        r"https?://((www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}|localhost)"
        r"(:[0-9]{2,4})?\b([-a-zA-Z0-9()@:%_+.~#?&/=,]*)",
        lambda x: f'<a href="{x.group(0)}">{x.group(0)}</a>',
        pretty_json_str,
    )

    return mark_safe(pretty_json_str)


@register.filter
def modulo(num, val):
    """Provides modulo functionality in templates."""
    return num % val


@register.filter
def url_parse(value):
    """Returns a url safe string."""
    if value is None:
        return ""

    if isinstance(value, int):
        value = str(value)

    return value.replace("/", "_sl_")


@register.filter
def url_deparse(value):
    """Deparse a url string."""
    if value is None:
        return ""

    # return urllib.parse.unquote(value)
    return value.replace("_sl_", "/")


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key in a template."""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def has_content(html):
    """Check if HTML has actual content beyond empty tags and whitespace entities."""
    if not html:
        return False
    text = re.sub(r'<[^>]+>', '', html)
    text = text.replace('&nbsp;', '').replace('&#160;', '')
    return bool(text.strip())
