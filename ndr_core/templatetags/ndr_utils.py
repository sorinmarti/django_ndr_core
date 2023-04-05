from django import template

register = template.Library()


@register.inclusion_tag('ndr_core/dummy.html')
def render_result(result_object, api_config):
    """Renders a result object using the appropriate template."""
    render_template = 'ndr_core/result_renderers/default_template.html'
    return {'template': render_template,
            'result': result_object}


@register.filter
def key_value(data_dict, key):
    """Provides key-value lookup functionality in templates."""
    if data_dict is None:
        return ''
    try:
        return data_dict[key]
    except KeyError:
        return ''


@register.filter
def modulo(num, val):
    """Provides modulo functionality in templates."""
    return num % val
