"""Template tags for the ndr_core app."""
import json
import re

from django import template
from django.db.models import Max
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from ndr_core.ndr_templatetags.template_string import TemplateString

register = template.Library()


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
        template_string = TemplateString(exp, result, show_errors=False)
        citation = template_string.get_formatted_string()
        citation = template_string.sanitize_html(citation)
        return mark_safe(citation)

    def create_grid(self, context, data, compact_view):
        """Creates a grid of result fields."""
        row_template = "ndr_core/result_renderers/elements/result_row.html"
        result_card_fields = self.search_config.resolve(
            context
        ).result_card_fields.filter(result_card_group=compact_view)
        max_row = result_card_fields.aggregate(Max("field_row"))

        card_grid_str = ""
        for row in range(max_row["field_row__max"]):
            row += 1
            fields = []
            for column in result_card_fields.filter(field_row=row).order_by(
                "field_column"
            ):
                field_html = self.create_field(column, data)
                fields.append(field_html)
            row_context = {"fields": fields}
            row_template_str = get_template(row_template).render(row_context)
            card_grid_str += row_template_str

        return mark_safe(card_grid_str)

    @staticmethod
    def create_field(field, data):
        """Creates a result field."""
        field_template = "ndr_core/result_renderers/elements/result_field.html"
        result_field = field.result_field
        template_string = TemplateString(
            result_field.rich_expression, data, show_errors=True
        )
        field_content = template_string.get_formatted_string()
        field_content = template_string.sanitize_html(field_content)

        field_context = {
            "size": field.field_size,
            "classes": result_field.field_classes,
            "field_content": field_content,
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

    return value.replace("/", "_sl_")


@register.filter
def url_deparse(value):
    """Deparse a url string."""
    if value is None:
        return ""

    # return urllib.parse.unquote(value)
    return value.replace("_sl_", "/")
