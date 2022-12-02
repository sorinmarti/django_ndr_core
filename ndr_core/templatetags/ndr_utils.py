from django import template

register = template.Library()


@register.inclusion_tag('ndr_core/dummy.html')
def render_result(result_object, api_config):
    render_template = 'ndr_core/result_renderers/historical_person.html'
    return {'template': render_template,
            'result': result_object}


@register.filter
def key_value(data_dict, key):
    if data_dict is None:
        return ''
    try:
        return data_dict[key]
    except KeyError:
        return ''
