import csv
from io import StringIO

from django.template.loader import render_to_string
from ndr_core.models import NdrCorePage


def get_nested_value(obj, path):
    """Get a nested value from an object."""
    try:
        for key in path.split("."):
            obj = obj[key]
    except KeyError:
        return "Key Not found"
    return obj


def create_csv_export_string(list_of_results, mapping):
    """Create a CSV export from a list of results and a mapping of fields to export."""
    output = StringIO()
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    lines = []
    title_rows = []

    for field in mapping:
        title_rows.append(field['header'])
    lines.append(title_rows)

    for result in list_of_results:
        rows = []
        for field in mapping:
            rows.append(get_nested_value(result, field['field']))
        lines.append(rows)

    writer.writerows(lines)

    string_output = output.getvalue().encode('utf-8')
    return string_output


def create_sitemap():
    pages = NdrCorePage.objects.all()
    rendered = render_to_string('ndr_core/utils/sitemap.xml', {'pages': pages})
    pass


def create_robots_txt():
    pass
