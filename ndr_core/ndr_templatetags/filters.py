import re
from datetime import datetime
import uuid
import json
from urllib.parse import urlparse
from django.templatetags.static import static
from django.utils.html import escape
from django.utils.safestring import mark_safe

from ndr_core.models import NdrCoreSearchField, NdrCorePage
from ndr_core.ndr_templatetags.abstract_filter import AbstractFilter
from ndr_core.ndr_templatetags.html_element import HTMLElement
from ndr_core.utils import get_nested_value


def get_get_filter_class(filter_name):
    """Returns the filter class."""
    if filter_name in ["lower", "upper", "title", "capitalize", "nl2br", "center"]:
        return StringFilter
    if filter_name == "bool":
        return BoolFilter
    if filter_name == "fieldify":
        return FieldTemplateFilter
    if filter_name == "fieldinfo":
        return FieldInfoTemplateFilter
    if filter_name == "list":
        return ListTemplateFilter
    if filter_name in ["badge", "pill"]:
        return BadgeTemplateFilter
    if filter_name == "img":
        return ImageTemplateFilter
    if filter_name == "file_display":
        return FileTemplateFilter
    if filter_name == "date":
        return DateFilter
    if filter_name == "format":
        return NumberFilter
    if filter_name == "readable":
        return ReadableNumberFilter
    if filter_name == "compact":
        return CompactNumberFilter
    if filter_name == "relative":
        return RelativeDateFilter
    if filter_name == "linkify":
        return LinkifyFilter
    if filter_name == "weblinks":
        return WeblinksFilter
    if filter_name == "orcid":
        return LinkifyFilter
    if filter_name == "iframe":
        return IframeFilter
    if filter_name == "default":
        return DefaultFilter
    if filter_name == "map":
        return MapFilter
    if filter_name in ["truncate", "text"]:
        return TextTruncateFilter
    if filter_name == "table":
        return TableTemplateFilter
    if filter_name == "datatable":
        return DatatableFilter
    if filter_name == "code":
        return CodeFilter
    if filter_name == "plotly":
        return PlotlyFilter
    if filter_name == "badges":
        return BadgesFilter

    raise ValueError(f"Filter {filter_name} not found.")


class StringFilter(AbstractFilter):
    """A class to represent a template filter."""

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return []

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns the formatted string."""
        if self.filter_name == "upper":
            return self.get_value().upper()
        if self.filter_name == "lower":
            return self.get_value().lower()
        if self.filter_name == "title":
            return self.get_value().title()
        if self.filter_name == "capitalize":
            return self.get_value().capitalize()
        if self.filter_name == "nl2br":
            return mark_safe(escape(self.get_value()).replace('\n', '<br>'))
        if self.filter_name == "center":
            return mark_safe(
                '<div style="width:fit-content;margin:0 auto;text-align:left;">'
                + str(self.get_value())
                + '</div>'
            )

        return self.get_value()


class BoolFilter(AbstractFilter):
    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return []

    def needed_options(self):
        return ["o0", "o1"]

    def get_rendered_value(self):
        true_value = "True"
        if self.get_configuration("o0"):
            true_value = self.get_configuration("o0")
        false_value = "False"
        if self.get_configuration("o1"):
            false_value = self.get_configuration("o1")

        if isinstance(self.value, bool):
            if self.value:
                return self.replace_key_values(true_value)
            return self.replace_key_values(false_value)

        if isinstance(self.value, str):
            if self.value.lower() == "true":
                return self.replace_key_values(true_value)
            return self.replace_key_values(false_value)

        return self.get_value()


class FieldTemplateFilter(AbstractFilter):
    """A class to represent a template filter."""

    field_value = ""
    search_field = None

    def __init__(self, filter_name, value, filter_configurations, data_context=None):
        super().__init__(filter_name, value, filter_configurations, data_context)
        try:
            self.search_field = NdrCoreSearchField.objects.get(
                field_name=self.get_configuration("o0")
            )
            try:
                self.field_value = self.search_field.get_choices_list_dict()[
                    self.value
                ][self.get_language_value_field_name()]
            except KeyError:
                self.field_value = self.value

        except NdrCoreSearchField.DoesNotExist:
            self.search_field = None

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return []

    def needed_options(self):
        return ["o0"]

    def get_rendered_value(self):
        """Returns the formatted string."""
        if not self.search_field:
            return self.get_value()

        return self.field_value


class FieldInfoTemplateFilter(AbstractFilter):
    """A class to represent a template filter that returns the info text of a field value."""

    field_info = ""
    search_field = None

    def __init__(self, filter_name, value, filter_configurations, data_context=None):
        super().__init__(filter_name, value, filter_configurations, data_context)
        try:
            self.search_field = NdrCoreSearchField.objects.get(
                field_name=self.get_configuration("o0")
            )
            try:
                self.field_info = self.search_field.get_choices_list_dict()[
                    self.value
                ][self.get_language_info_field_name()]
            except KeyError:
                self.field_info = ""

        except NdrCoreSearchField.DoesNotExist:
            self.search_field = None

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return []

    def needed_options(self):
        return ["o0"]

    def get_rendered_value(self):
        """Returns the info text."""
        if not self.search_field:
            return ""

        return self.field_info


class ListTemplateFilter(AbstractFilter):
    """A class to represent a template filter that renders lists as HTML ul or ol."""

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["type", "class"]

    def needed_options(self):
        return []

    def processes_list_as_whole(self):
        """This filter needs to process the entire list at once."""
        return True

    def get_rendered_value(self):
        """Returns the formatted string."""
        value = self.value

        if not isinstance(value, list):
            return self.get_value()

        if len(value) == 0:
            return ""

        list_type = self.get_configuration("type") or "ul"
        list_class = self.get_configuration("class") or ""

        class_attr = f' class="{list_class}"' if list_class else ""

        if list_type == "ol":
            html = f"<ol{class_attr}>"
        else:
            html = f"<ul{class_attr}>"

        for item in value:
            if isinstance(item, dict):
                item_str = str(item)
            else:
                item_str = str(item)
            html += f"<li>{item_str}</li>"

        if list_type == "ol":
            html += "</ol>"
        else:
            html += "</ul>"

        return html


class BadgeTemplateFilter(AbstractFilter):
    """A class to represent a template filter."""

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["field", "color", "bg", "tt"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns the formatted string."""

        badge_element = HTMLElement("span")
        badge_element.add_attribute("class", "badge")
        badge_element.add_attribute("class", "badge-auto-text")
        badge_element.add_attribute("class", "font-weight-normal")

        if self.get_configuration("tt"):
            badge_element.add_attribute("data-bs-toggle", "tooltip")
            badge_element.add_attribute("data-bs-placement", "top")
            if not self.get_configuration("field"):
                # Replace placeholders in tooltip text
                tt_text = self.get_configuration("tt")
                if self.data_context:
                    tt_text = self.replace_placeholders(tt_text)
                badge_element.add_attribute("title", tt_text)

        field_options = None
        if self.get_configuration("field"):
            # The 'field' option is set. Try to get a translated value from the NDRCoreSearchField
            try:
                field = NdrCoreSearchField.objects.get(
                    field_name=self.get_configuration("field")
                )
                all_field_options = field.get_choices_list_dict()
                field_options = all_field_options[self.value]

                if not field_options['is_printable']:
                    return None

                badge_element.add_content(
                    field_options[self.get_language_value_field_name()]
                )
                if self.get_configuration("tt"):
                    tt_content = self.get_configuration("tt")
                    if tt_content == "__field__":
                        tt_text = field_options[self.get_language_info_field_name()]
                    else:
                        # Replace placeholders in tooltip text
                        tt_text = tt_content
                        if self.data_context:
                            tt_text = self.replace_placeholders(tt_text)
                    badge_element.add_attribute("title", tt_text)
            except NdrCoreSearchField.DoesNotExist:
                badge_element.add_content("Field not found")  # TODO: internationalize
        else:
            badge_element.add_content(self.get_value())

        if self.get_configuration("color"):
            badge_element.manage_color_attribute(
                "color", self.get_configuration("color"), self.get_value(), field_options
            )
        if self.get_configuration("bg"):
            badge_element.manage_color_attribute(
                "bg", self.get_configuration("bg"), self.get_value(), field_options
            )

        return str(badge_element)

    def replace_placeholders(self, text):
        """Replace [variable] placeholders in the text with actual values."""
        # Find all [variable] patterns
        placeholders = re.findall(r'\[([^\]]+)\]', text)

        # Replace each placeholder with its value
        for placeholder in placeholders:
            try:
                # Get the value from the data context
                placeholder_value = get_nested_value(self.data_context, placeholder)
                if placeholder_value is not None:
                    # Handle arrays - take first element if it's a list
                    if isinstance(placeholder_value, list) and len(placeholder_value) > 0:
                        placeholder_value = placeholder_value[0]
                    text = text.replace(f'[{placeholder}]', str(placeholder_value))
                else:
                    text = text.replace(f'[{placeholder}]', '')
            except:
                # If placeholder can't be resolved, remove it
                text = text.replace(f'[{placeholder}]', '')

        return text


class ImageTemplateFilter(AbstractFilter):

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["url", "iiif_resize", "iiif_full", "width", "height", "alt", "class", "style", "title"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        # Check the base value first - this determines if we should show default
        value = self.get_value()
        if value == self.get_default_value():
            # If the value is the default, return it
            return value

        # Determine the image URL
        if self.get_configuration("url"):
            # Use provided URL (with potential placeholders)
            url = self.get_configuration("url")
            if self.data_context:
                url = self.replace_placeholders(url)
        else:
            # Use the filter value as URL
            url = str(value)

        # Handle IIIF resize if specified
        # IIIF URL structure: /{region}/{size}/{rotation}/{quality}.{format}
        # Replace the {size} segment (max, full, pct:N, w,h, !w,h, w,, ,h)
        # with pct:{value}, regardless of what size was used originally.
        if self.get_configuration("iiif_resize") and url:
            pct = self.get_configuration("iiif_resize")
            url = re.sub(
                r'/(full|[\d,!]+)/(max|full|pct:[\d.]+|!?[\d]+,[\d]*)(/\d+/(?:default|native|bitonal|gray|color)\.)',
                rf'/\1/pct:{pct}\3',
                url,
            )

        if self.get_configuration("iiif_full") and url:
            if self.get_configuration("iiif_full").lower() in ["true", "1", "yes"]:
                url = re.sub(r'/\d+,\d+,\d+,\d+/', '/full/', url)

        # Create the image element
        element = HTMLElement("img")
        element.add_attribute("src", url)

        # Set default attributes
        element.add_attribute("class", "img-fluid")
        element.add_attribute("alt", "Image")

        # Add optional attributes
        if self.get_configuration("width"):
            element.add_attribute("width", self.get_configuration("width"))

        if self.get_configuration("height"):
            element.add_attribute("height", self.get_configuration("height"))

        if self.get_configuration("alt"):
            element.add_attribute("alt", self.get_configuration("alt"))

        if self.get_configuration("class"):
            # Replace default class if custom class provided
            element.add_attribute("class", self.get_configuration("class"))

        if self.get_configuration("style"):
            element.add_attribute("style", self.get_configuration("style"))

        if self.get_configuration("title"):
            element.add_attribute("title", self.get_configuration("title"))

        return str(element)

    def replace_placeholders(self, url):
        """Replace [variable] placeholders in the URL with actual values."""
        import re
        from ndr_core.utils import get_nested_value

        # Find all [variable] patterns
        placeholders = re.findall(r'\[([^\]]+)\]', url)

        # Replace each placeholder with its value
        for placeholder in placeholders:
            try:
                # Get the value from the data context
                placeholder_value = get_nested_value(self.data_context, placeholder)
                if placeholder_value is not None:
                    # Handle arrays - take first element if it's a list
                    if isinstance(placeholder_value, list) and len(placeholder_value) > 0:
                        placeholder_value = placeholder_value[0]
                    url = url.replace(f'[{placeholder}]', str(placeholder_value))
                else:
                    url = url.replace(f'[{placeholder}]', '')
            except:
                # If placeholder can't be resolved, remove it
                url = url.replace(f'[{placeholder}]', '')

        return url


class FileTemplateFilter(AbstractFilter):
    """Filter for displaying text file content previews (txt, json, md, xml, csv, etc.)"""

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["url", "type", "max_lines", "max_height", "class", "style", "show_line_numbers"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        # Check the base value first - this determines if we should show default
        value = self.get_value()
        if value == self.get_default_value():
            # If the value is the default, return it
            return value

        # Determine the file URL/path
        if self.get_configuration("url"):
            # Use provided URL (with potential placeholders)
            file_path = self.get_configuration("url")
            if self.data_context:
                file_path = self.replace_placeholders(file_path)
        else:
            # Use the filter value as path
            file_path = str(value)

        # Get file extension
        file_ext = self.get_file_extension(file_path)

        # Override file type if specified
        if self.get_configuration("type"):
            file_ext = self.get_configuration("type").lower()

        # Generate preview based on file type
        return self.generate_text_file_preview(file_path, file_ext)

    def get_file_extension(self, file_path):
        """Extract file extension from file path."""
        import os
        if file_path:
            # Remove query parameters
            path = file_path.split('?')[0]
            return os.path.splitext(path)[1].lower().lstrip('.')
        return ''

    def read_file_content(self, file_path):
        """Read file content from local path or URL."""
        import os
        from django.conf import settings

        try:
            # If it's a URL (starts with http/https), we can't read it directly server-side
            if file_path.startswith('http://') or file_path.startswith('https://'):
                # Return placeholder - actual content will be loaded via JavaScript
                return None

            # Handle Django file fields
            if hasattr(file_path, 'read'):
                file_path.seek(0)
                content = file_path.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                return content

            # Handle file paths relative to MEDIA_ROOT
            if not os.path.isabs(file_path):
                file_path = os.path.join(settings.MEDIA_ROOT, file_path)

            # Read local file
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    max_lines = int(self.get_configuration("max_lines") or 1000)
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            lines.append(f"... (truncated after {max_lines} lines)")
                            break
                        lines.append(line.rstrip('\n'))
                    return '\n'.join(lines)

            return None

        except Exception as e:
            return f"Error reading file: {str(e)}"

    def generate_text_file_preview(self, file_path, file_ext):
        """Generate text file content preview."""

        # Read file content
        content = self.read_file_content(file_path)

        if content is None:
            # For URLs, use JavaScript to fetch content
            return self.generate_ajax_preview(file_path, file_ext)

        # Generate container
        container = HTMLElement("div")
        container.add_attribute("class", "file-preview file-preview-text")

        if self.get_configuration("class"):
            container.add_attribute("class", self.get_configuration("class"))

        # Determine language/format for syntax highlighting
        language = self.get_language_for_highlighting(file_ext)

        # Generate header
        filename = file_path.split('/')[-1]
        header = f'<div style="padding: 8px 12px; background: #e9ecef; border-bottom: 1px solid #dee2e6; font-weight: bold; font-size: 0.9em;">{filename} <span style="color: #6c757d;">({file_ext.upper()})</span></div>'

        # Generate content display
        max_height = self.get_configuration("max_height") or "400px"
        show_line_numbers = self.get_configuration("show_line_numbers")

        if file_ext == 'json':
            # Pretty print JSON
            content_display = self.format_json_content(content, max_height, show_line_numbers)
        else:
            # Display as preformatted text
            content_display = self.format_text_content(content, max_height, show_line_numbers, language)

        container.add_content(header)
        container.add_content(content_display)

        # Add border and styling
        container.add_attribute("style", "border: 1px solid #dee2e6; border-radius: 4px; overflow: hidden;")
        if self.get_configuration("style"):
            container.add_attribute("style", self.get_configuration("style"))

        return str(container)

    def generate_ajax_preview(self, url, file_ext):
        """Generate preview that loads content via JavaScript for remote URLs."""
        preview_id = f"file-preview-{uuid.uuid4().hex[:8]}"

        container = HTMLElement("div")
        container.add_attribute("class", "file-preview file-preview-ajax")
        container.add_attribute("id", preview_id)

        filename = url.split('/')[-1]
        header = f'<div style="padding: 8px 12px; background: #e9ecef; border-bottom: 1px solid #dee2e6; font-weight: bold; font-size: 0.9em;">{filename} <span style="color: #6c757d;">({file_ext.upper()})</span></div>'

        loading = f'<div style="padding: 20px; text-align: center; color: #6c757d;">Loading file content...</div>'

        max_height = self.get_configuration("max_height") or "400px"

        script = f'''
        <script>
        (function() {{
            fetch('{url}')
                .then(response => response.text())
                .then(content => {{
                    const container = document.getElementById('{preview_id}');
                    const contentDiv = container.querySelector('.file-content');
                    contentDiv.innerHTML = '<pre style="margin: 0; padding: 12px; max-height: {max_height}; overflow: auto; background: #f8f9fa;"><code>' + content.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</code></pre>';
                }})
                .catch(error => {{
                    const container = document.getElementById('{preview_id}');
                    const contentDiv = container.querySelector('.file-content');
                    contentDiv.innerHTML = '<div style="padding: 20px; color: #dc3545;">Error loading file: ' + error.message + '</div>';
                }});
        }})();
        </script>
        '''

        container.add_content(header)
        container.add_content('<div class="file-content">' + loading + '</div>')
        container.add_content(script)

        container.add_attribute("style", "border: 1px solid #dee2e6; border-radius: 4px; overflow: hidden;")

        return str(container)

    def format_json_content(self, content, max_height, show_line_numbers):
        """Format JSON content with pretty printing."""
        try:
            # Try to parse and pretty print JSON
            parsed = json.loads(content)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        except:
            # If parsing fails, use original content
            formatted = content

        # Escape HTML
        from html import escape
        formatted = escape(formatted)

        if show_line_numbers and show_line_numbers.lower() in ["true", "1", "yes"]:
            lines = formatted.split('\n')
            line_numbers = '\n'.join(str(i+1) for i in range(len(lines)))
            return f'''
            <div style="display: flex; max-height: {max_height}; overflow: auto; background: #f8f9fa;">
                <pre style="margin: 0; padding: 12px; background: #e9ecef; color: #6c757d; text-align: right; user-select: none; border-right: 1px solid #dee2e6;"><code>{line_numbers}</code></pre>
                <pre style="margin: 0; padding: 12px; flex: 1;"><code>{formatted}</code></pre>
            </div>
            '''
        else:
            return f'<pre style="margin: 0; padding: 12px; max-height: {max_height}; overflow: auto; background: #f8f9fa;"><code>{formatted}</code></pre>'

    def format_text_content(self, content, max_height, show_line_numbers, language):
        """Format text content with optional line numbers."""
        from html import escape
        content = escape(content)

        if show_line_numbers and show_line_numbers.lower() in ["true", "1", "yes"]:
            lines = content.split('\n')
            line_numbers = '\n'.join(str(i+1) for i in range(len(lines)))
            return f'''
            <div style="display: flex; max-height: {max_height}; overflow: auto; background: #f8f9fa;">
                <pre style="margin: 0; padding: 12px; background: #e9ecef; color: #6c757d; text-align: right; user-select: none; border-right: 1px solid #dee2e6;"><code>{line_numbers}</code></pre>
                <pre style="margin: 0; padding: 12px; flex: 1;"><code>{content}</code></pre>
            </div>
            '''
        else:
            return f'<pre style="margin: 0; padding: 12px; max-height: {max_height}; overflow: auto; background: #f8f9fa;"><code>{content}</code></pre>'

    def get_language_for_highlighting(self, file_ext):
        """Map file extension to programming language for potential syntax highlighting."""
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'html': 'html',
            'css': 'css',
            'json': 'json',
            'xml': 'xml',
            'md': 'markdown',
            'yaml': 'yaml',
            'yml': 'yaml',
            'sql': 'sql',
            'sh': 'bash',
            'bash': 'bash',
        }
        return language_map.get(file_ext, 'text')

    def replace_placeholders(self, text):
        """Replace [variable] placeholders in the text with actual values."""
        import re
        from ndr_core.utils import get_nested_value

        # Find all [variable] patterns
        placeholders = re.findall(r'\[([^\]]+)\]', text)

        # Replace each placeholder with its value
        for placeholder in placeholders:
            try:
                # Get the value from the data context
                placeholder_value = get_nested_value(self.data_context, placeholder)
                if placeholder_value is not None:
                    # Handle arrays - take first element if it's a list
                    if isinstance(placeholder_value, list) and len(placeholder_value) > 0:
                        placeholder_value = placeholder_value[0]
                    text = text.replace(f'[{placeholder}]', str(placeholder_value))
                else:
                    text = text.replace(f'[{placeholder}]', '')
            except:
                # If placeholder can't be resolved, remove it
                text = text.replace(f'[{placeholder}]', '')

        return text


class DateFilter(AbstractFilter):
    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["format"]

    def needed_options(self):
        return ["o0"]

    def get_rendered_value(self):
        """Returns the formatted string."""
        common_formats = ["%Y-%m-%d"]
        if self.get_configuration("format"):
            common_formats = [self.get_configuration("format")]

        for d_format in common_formats:
            try:
                date_object = datetime.strptime(self.value, d_format)
                return date_object.strftime(self.get_configuration("o0"))
            except ValueError:
                pass

        return self.get_value()


class NumberFilter(AbstractFilter):
    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return []

    def needed_options(self):
        return ['o0']

    def get_rendered_value(self):
        """Returns the formatted string."""
        value = self.get_value()

        # Try to convert to number (int or float)
        try:
            # First try as float to preserve decimal values
            if isinstance(value, str):
                # Check if it contains a decimal point
                if '.' in value:
                    number_value = float(value)
                else:
                    number_value = int(value)
            elif isinstance(value, (int, float)):
                number_value = value
            else:
                return self.get_value()

            # Apply the format specification
            return ("{:" + self.get_configuration('o0') + "}").format(number_value)
        except (ValueError, TypeError):
            return self.get_value()

    def get_value(self):
        """Returns the formatted string."""
        return self.value


class LinkifyFilter(AbstractFilter):
    """A class to represent a linkify template filter that wraps content in an <a> tag."""

    def needed_attributes(self):
        return []  # No required attributes now - we have multiple ways to specify URL

    def allowed_attributes(self):
        return ["url", "page", "page_url", "params", "target", "class", "title", "rel", "display"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns the content wrapped in an <a> tag."""

        # Handle ORCID-specific case
        if self.filter_name == "orcid":
            orcid = self.get_value()
            orcid_pattern = r"^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$"
            if re.match(orcid_pattern, orcid):
                orcid_url = f"https://orcid.org/{orcid}"
                orcid_icon_url = static('ndr_core/images/orcid.svg')
                return f"""
                        <a href="{orcid_url}" target="_blank" class="orcid-link" rel="noopener noreferrer">
                            <img src="{orcid_icon_url}" alt="ORCID" style="width: 16px; height: 16px; vertical-align: middle;">
                            {orcid}
                        </a>
                        """
            else:
                return f"<span class='text-danger'>Invalid ORCID: {orcid}</span>"

        # Determine the URL from various sources
        url = self.build_url()
        if not url:
            return self.get_value()

        # Add GET parameters if specified
        url = self.add_get_parameters(url)

        # Create the link element
        link_element = HTMLElement("a")
        link_element.add_attribute("href", url)

        # Add optional attributes
        if self.get_configuration("target"):
            target = self.get_configuration("target")
            if target == "blank":
                target = "_blank"
            link_element.add_attribute("target", target)

        # Handle display attribute for button styling
        css_classes = []
        if self.get_configuration("class"):
            css_classes.append(self.get_configuration("class"))

        display_type = self.get_configuration("display")
        if display_type == "button":
            # Add Bootstrap button classes
            css_classes.append("btn btn-primary")

        if css_classes:
            link_element.add_attribute("class", " ".join(css_classes))

        if self.get_configuration("title"):
            link_element.add_attribute("title", self.get_configuration("title"))

        if self.get_configuration("rel"):
            link_element.add_attribute("rel", self.get_configuration("rel"))
        elif self.get_configuration("target") == "_blank":
            # Add security attribute for external links
            link_element.add_attribute("rel", "noopener noreferrer")

        # Add the content (which could be the result of previous filters)
        link_element.add_content(str(self.get_value()))

        return str(link_element)

    def build_url(self):
        """Build URL from various configuration options."""
        # Option 1: Direct URL with placeholders
        if self.get_configuration("url"):
            url = self.get_configuration("url")
            if self.data_context:
                url = self.replace_placeholders(url)
            return url

        # Option 2: Use page_url attribute - expects page object with url() method
        if self.get_configuration("page_url"):
            page_ref = self.get_configuration("page_url")
            if self.data_context:
                try:
                    # Get page object from data context
                    page_obj = get_nested_value(self.data_context, page_ref)
                    if page_obj and hasattr(page_obj, 'url'):
                        return page_obj.url()
                except:
                    pass

        # Option 3: Page view_name or ID lookup
        if self.get_configuration("page"):
            page_ref = self.get_configuration("page")

            # Replace placeholders in page reference
            if self.data_context:
                page_ref = self.replace_placeholders(page_ref)

            try:
                # Try to get page by view_name first
                try:
                    page = NdrCorePage.objects.get(view_name=page_ref)
                except NdrCorePage.DoesNotExist:
                    # Try by ID if it's numeric
                    if page_ref.isdigit():
                        page = NdrCorePage.objects.get(pk=int(page_ref))
                    else:
                        return None

                # Use the page's url() method
                return page.url()
            except (NdrCorePage.DoesNotExist, ValueError):
                return None

        return None

    def add_get_parameters(self, url):
        """Add GET parameters to URL if specified."""
        if not self.get_configuration("params"):
            return url

        params_config = self.get_configuration("params")

        # Replace placeholders in params if data context is available
        if self.data_context:
            params_config = self.replace_placeholders(params_config)

        # Parse parameters (format: "param1=value1,param2=value2")
        try:
            from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

            # Parse the current URL
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)

            # Parse new parameters
            param_pairs = params_config.split(',')
            for pair in param_pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Add to query params (convert to list format expected by parse_qs)
                    query_params[key] = [value]

            # Rebuild URL with new query parameters
            new_query = urlencode(query_params, doseq=True)
            new_parsed = parsed_url._replace(query=new_query)
            return urlunparse(new_parsed)
        except:
            # If parsing fails, just append parameters with ? or &
            separator = '&' if '?' in url else '?'
            return f"{url}{separator}{params_config}"

    def replace_placeholders(self, url):
        """Replace [variable] placeholders in the URL with actual values."""

        # Find all [variable] patterns
        placeholders = re.findall(r'\[([^\]]+)\]', url)

        # Replace each placeholder with its value
        for placeholder in placeholders:
            try:
                # Get the value from the data context
                # This assumes self.data_context is available (you might need to pass this)
                placeholder_value = get_nested_value(self.data_context, placeholder)
                if placeholder_value is not None:
                    url = url.replace(f'[{placeholder}]', str(placeholder_value))
                else:
                    url = url.replace(f'[{placeholder}]', '')
            except:
                # If placeholder can't be resolved, leave it as is or remove it
                url = url.replace(f'[{placeholder}]', '')

        return url


class WeblinksFilter(AbstractFilter):
    """A filter to generate a list of favicons linking to the provided URLs."""

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["class", "style", "target"]

    def needed_options(self):
        return []

    def processes_list_as_whole(self):
        """This filter processes the entire list as a whole."""
        return True

    def get_rendered_value(self):
        """Generates a list of favicons linking to the provided URLs."""
        value = self.get_value()

        if not isinstance(value, list):
            return value

        if not value:
            return f"<span class='text-muted'>No URLs provided</span>"

        # Default attributes
        link_target = self.get_configuration("target") or "_blank"
        link_class = self.get_configuration("class") or "weblink"
        link_style = self.get_configuration("style") or ""
        default_icon_config = self.get_configuration("default_icon")
        default_icon = default_icon_config if default_icon_config else static('ndr_core/images/not-found-favicon.ico')

        # Generate HTML for each URL
        links_html = []
        for url in value:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            favicon_url = f"{base_url}/favicon.ico"
            link_html = f"""
                       <a href="{url}" target="{link_target}" class="{link_class}" style="{link_style}"
                          data-bs-toggle="tooltip" title="{url}">
                           <img src="{favicon_url}" alt="{parsed.netloc}" 
                                onerror="this.onerror=null;this.src='{default_icon}';" 
                                style="width: 16px; height: 16px; vertical-align: middle;">
                       </a>
                       """
            links_html.append(link_html)

        # Wrap in a container
        return f"<div>{''.join(links_html)}</div>"

class IframeFilter(AbstractFilter):
    """A class to represent an iframe template filter that embeds content in an <iframe> tag."""

    def __init__(self, filter_name, value, filter_configurations, data_context=None):
        super().__init__(filter_name, value, filter_configurations, data_context)

    def needed_attributes(self):
        return []  # No required attributes

    def allowed_attributes(self):
        return ["width", "height", "title", "frameborder", "allowfullscreen",
                "sandbox", "loading", "referrerpolicy", "class", "style", "src"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns an iframe element with the value as src or embedded content."""

        # Get the source URL - could be the filter value or from src parameter
        src_url = self.get_configuration("src") or self.get_value()

        # Replace placeholders in URL if data context is available
        if self.data_context and src_url:
            src_url = self.replace_placeholders(str(src_url))

        # Create the iframe element
        iframe_element = HTMLElement("iframe")
        iframe_element.add_attribute("src", src_url)

        # Set default attributes for security and usability
        iframe_element.add_attribute("frameborder", "0")
        iframe_element.add_attribute("loading", "lazy")

        # Add optional attributes with defaults
        width = self.get_configuration("width") or "100%"
        height = self.get_configuration("height") or "400"
        iframe_element.add_attribute("width", width)
        iframe_element.add_attribute("height", height)

        # Add title for accessibility
        title = self.get_configuration("title") or "Embedded content"
        iframe_element.add_attribute("title", title)

        # Handle security attributes
        if self.get_configuration("sandbox"):
            iframe_element.add_attribute("sandbox", self.get_configuration("sandbox"))

        if self.get_configuration("allowfullscreen"):
            if self.get_configuration("allowfullscreen").lower() in ["true", "1", "yes"]:
                iframe_element.add_attribute("allowfullscreen", "")

        # Handle loading attribute
        if self.get_configuration("loading"):
            iframe_element.add_attribute("loading", self.get_configuration("loading"))

        # Handle referrer policy
        if self.get_configuration("referrerpolicy"):
            iframe_element.add_attribute("referrerpolicy", self.get_configuration("referrerpolicy"))

        # Add CSS class if specified
        if self.get_configuration("class"):
            iframe_element.add_attribute("class", self.get_configuration("class"))

        # Add inline styles if specified
        if self.get_configuration("style"):
            iframe_element.add_attribute("style", self.get_configuration("style"))

        # Override frameborder if explicitly set
        if self.get_configuration("frameborder"):
            iframe_element.add_attribute("frameborder", self.get_configuration("frameborder"))

        return str(iframe_element)

    def replace_placeholders(self, url):
        """Replace [variable] placeholders in the URL with actual values."""
        import re
        from ndr_core.utils import get_nested_value

        # Find all [variable] patterns
        placeholders = re.findall(r'\[([^\]]+)\]', url)

        # Replace each placeholder with its value
        for placeholder in placeholders:
            try:
                # Get the value from the data context
                placeholder_value = get_nested_value(self.data_context, placeholder)
                if placeholder_value is not None:
                    url = url.replace(f'[{placeholder}]', str(placeholder_value))
                else:
                    url = url.replace(f'[{placeholder}]', '')
            except:
                # If placeholder can't be resolved, remove it
                url = url.replace(f'[{placeholder}]', '')

        return url



class DefaultFilter(AbstractFilter):
    """A filter that just returns the value as-is. Used when you only want to specify a default value."""

    def check_configuration(self):
        pass  # Intentionally permissive — accepts value=, o0, or nothing

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["value"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns the value as-is."""
        return self.get_value()



class MapFilter(AbstractFilter):
    """A filter to display coordinates as an interactive Leaflet map widget."""

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["width", "height", "zoom", "marker", "popup", "groups", "colors", "legend"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns a Leaflet map widget HTML."""
        value = self.get_value()
        
        # Extract markers from various input formats
        markers = self.extract_markers(value)
        
        if not markers:
            if self.get_configuration("default"):
                # If no markers found, a default value might be specified
                return self.get_configuration("default")
            return f"<span class=\"text-muted\">No valid coordinates found: {value}</span>"
        
        # Generate unique ID for this map
        map_id = f"map_{uuid.uuid4().hex[:8]}"
        
        # Configuration
        width = self.get_configuration("width") or "300px"
        height = self.get_configuration("height") or "200px" 
        zoom = self.get_configuration("zoom") or "10"  # Lower default zoom for multiple markers
        show_marker = self.get_configuration("marker") != "false"
        show_legend = self.get_configuration("legend") != "false"  # Show legend by default
        
        # Calculate center and bounds for multiple markers
        if len(markers) == 1:
            center_lat, center_lng = markers[0]["latitude"], markers[0]["longitude"]
            fit_bounds = False
        else:
            center_lat = sum(m["latitude"] for m in markers) / len(markers)
            center_lng = sum(m["longitude"] for m in markers) / len(markers)
            fit_bounds = True
        
        # Generate markers JavaScript with colors
        markers_js = ""
        if show_marker:
            for i, marker in enumerate(markers):
                popup_text = marker.get("popup", f"Location {i+1}: {marker['latitude']}, {marker['longitude']}")
                color = marker.get("color", "red")
                
                # Properly escape quotes and newlines for JavaScript
                popup_text = popup_text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')
                
                # Create colored marker
                markers_js += f"""
                var icon_{i} = L.divIcon({{
                    className: 'custom-marker-{color}',
                    html: '<div style="background-color: {color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.4);"></div>',
                    iconSize: [16, 16],
                    iconAnchor: [8, 8]
                }});
                L.marker([{marker["latitude"]}, {marker["longitude"]}], {{icon: icon_{i}}}).addTo(map).bindPopup("{popup_text}");
                """
        
        # Generate bounds JavaScript for multiple markers
        bounds_js = ""
        if fit_bounds and len(markers) > 1:
            bounds_coords = [[m["latitude"], m["longitude"]] for m in markers]
            bounds_js = f"var bounds = {json.dumps(bounds_coords)}; map.fitBounds(bounds, {{padding: [10, 10]}});"
        
        # Generate legend HTML
        legend_html = ""
        if show_legend and len(markers) > 1:
            # Get unique groups and colors
            groups = {}
            for marker in markers:
                group_name = marker.get("group", "default")
                group_color = marker.get("color", "red")
                if group_name not in groups:
                    groups[group_name] = group_color
            
            if len(groups) > 1:  # Only show legend if there are multiple groups
                legend_items = []
                for group_name, color in groups.items():
                    display_name = group_name.replace("_", " ").title() if group_name != "default" else "Location"
                    legend_items.append(f"""
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        <div style="width: 12px; height: 12px; background-color: {color}; border-radius: 50%; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.4); margin-right: 8px;"></div>
                        <span style="font-size: 12px; color: #333;">{display_name}</span>
                    </div>
                    """)
                
                legend_html = f"""
                <div style="background: white; border: 1px solid #ccc; border-radius: 4px; padding: 8px; margin-top: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);">
                    <div style="font-size: 13px; font-weight: bold; margin-bottom: 6px; color: #555;">Legend</div>
                    {"".join(legend_items)}
                </div>
                """
        
        # Generate the HTML
        return f"""
        <div>
            <div id="{map_id}" style="width: {width}; height: {height}; border: 1px solid #ccc; border-radius: 4px;"></div>
            {legend_html}
        </div>
        <script>
        (function() {{
            // Load Leaflet if not already loaded
            if (typeof L === "undefined") {{
                var link = document.createElement("link");
                link.rel = "stylesheet";
                link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
                document.head.appendChild(link);
                
                var script = document.createElement("script");
                script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
                script.onload = function() {{ initMap_{map_id}(); }};
                document.head.appendChild(script);
            }} else {{
                initMap_{map_id}();
            }}
            
            function initMap_{map_id}() {{
                var map = L.map("{map_id}").setView([{center_lat}, {center_lng}], {zoom});
                
                L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
                    attribution: "&copy; OpenStreetMap contributors"
                }}).addTo(map);
                
                {markers_js}
                
                {bounds_js}
            }}
        }})();
        </script>
        """
    
    def extract_markers(self, value):
        """Extract multiple markers from various input formats."""
        markers = []
        groups_config = self.get_configuration("groups")
        default_colors = ["red", "blue", "green", "orange", "purple", "yellow", "pink", "gray"]
        
        if groups_config:
            # Handle groups configuration: "Founded:12321:red,Liquidated:12322:blue,Work:12331:green"
            groups = self.parse_groups_config(groups_config, value)
            for group in groups:
                group_markers = self.extract_group_markers(group["data"], group["name"], group["color"])
                markers.extend(group_markers)
        else:
            # Regular extraction for backward compatibility
            if isinstance(value, dict):
                # Initialize is_object_subs flag
                is_object_subs = False

                # Check for direct latitude/longitude coordinates first
                if "latitude" in value and "longitude" in value:
                    # Single coordinate dict - create marker directly
                    try:
                        lat = float(value["latitude"])
                        lng = float(value["longitude"])

                        # Create popup with available info
                        popup_parts = []
                        if "name" in value:
                            popup_parts.append(f"Name: {value['name']}")
                        if "transcription" in value:
                            popup_parts.append(f"Transcription: {value['transcription']}")
                        popup_text = " | ".join(popup_parts) if popup_parts else f"Coordinates: {lat}, {lng}"

                        markers.append({
                            "latitude": lat,
                            "longitude": lng,
                            "popup": popup_text,
                            "group": "default",
                            "color": default_colors[0]
                        })
                    except (ValueError, TypeError):
                        pass  # Continue to other extraction methods
                # Check for nested coordinates structure
                elif "coordinates" in value and isinstance(value["coordinates"], dict):
                    coords = value["coordinates"]
                    try:
                        lat, lng = None, None
                        if "lat" in coords and "lon" in coords:
                            lat = float(coords["lat"])
                            lng = float(coords["lon"])
                        elif "latitude" in coords and "longitude" in coords:
                            lat = float(coords["latitude"])
                            lng = float(coords["longitude"])

                        if lat is not None and lng is not None:
                            # Create popup with available info
                            popup_parts = []
                            if "name" in value:
                                popup_parts.append(f"Name: {value['name']}")
                            if "city" in value:
                                popup_parts.append(f"City: {value['city']}")
                            if "country" in value:
                                popup_parts.append(f"Country: {value['country']}")
                            if "transcription" in value:
                                popup_parts.append(f"Transcription: {value['transcription']}")
                            popup_text = " | ".join(popup_parts) if popup_parts else f"Coordinates: {lat}, {lng}"

                            markers.append({
                                "latitude": lat,
                                "longitude": lng,
                                "popup": popup_text,
                                "group": "default",
                                "color": default_colors[0]
                            })
                    except (ValueError, TypeError):
                        pass  # Continue to other extraction methods
                # Check if this looks like object_subs structure with multiple groups
                elif all(isinstance(v, list) for v in value.values() if isinstance(v, (list, dict))):
                    is_object_subs = True

                if "type" in value and "coordinates" in value:
                    # Single geometry object
                    lat, lng = self.extract_coordinates(value)
                    if lat is not None and lng is not None:
                        markers.append({
                            "latitude": lat,
                            "longitude": lng,
                            "popup": self.get_configuration("popup") or f"Coordinates: {lat}, {lng}",
                            "group": "default",
                            "color": default_colors[0]
                        })
                elif "geometry" in value:
                    # Single object with geometry field
                    marker = self.extract_single_marker(value, "0", "default", default_colors[0])
                    if marker:
                        markers.append(marker)
                elif is_object_subs:
                    # Auto-detect groups from object_subs structure
                    for i, (key, objects) in enumerate(value.items()):
                        color = default_colors[i % len(default_colors)]
                        group_markers = self.extract_group_markers(objects, key, color)
                        markers.extend(group_markers)
                else:
                    # Handle as regular dict
                    for key, objects in value.items():
                        if isinstance(objects, list):
                            for obj in objects:
                                marker = self.extract_single_marker(obj, key, "default", default_colors[0])
                                if marker:
                                    markers.append(marker)
                        else:
                            marker = self.extract_single_marker(objects, key, "default", default_colors[0])
                            if marker:
                                markers.append(marker)
            elif isinstance(value, list):
                # Direct list of objects
                for i, obj in enumerate(value):
                    marker = self.extract_single_marker(obj, str(i), "default", default_colors[0])
                    if marker:
                        markers.append(marker)
            else:
                # Single coordinates
                lat, lng = self.extract_coordinates(value)
                if lat is not None and lng is not None:
                    markers.append({
                        "latitude": lat,
                        "longitude": lng,
                        "popup": self.get_configuration("popup") or f"Coordinates: {lat}, {lng}",
                        "group": "default",
                        "color": default_colors[0]
                    })
        
        return markers
    
    def parse_groups_config(self, groups_config, data):
        """Parse groups configuration string."""
        groups = []
        if not isinstance(data, dict):
            return groups
        
        # Remove surrounding quotes if present
        if groups_config.startswith('"') and groups_config.endswith('"'):
            groups_config = groups_config[1:-1]
        elif groups_config.startswith("'") and groups_config.endswith("'"):
            groups_config = groups_config[1:-1]
            
        group_parts = groups_config.split(',')
        for part in group_parts:
            elements = part.strip().split(':')
            if len(elements) >= 2:
                name = elements[0].strip()
                key = elements[1].strip()
                color = elements[2].strip() if len(elements) > 2 else "red"
                
                if key in data:
                    groups.append({
                        "name": name,
                        "data": data[key],
                        "color": color
                    })
        return groups
    
    def extract_group_markers(self, data, group_name, color):
        """Extract markers for a specific group."""
        markers = []
        if isinstance(data, list):
            for i, obj in enumerate(data):
                marker = self.extract_single_marker(obj, f"{group_name}_{i}", group_name, color)
                if marker:
                    markers.append(marker)
        else:
            marker = self.extract_single_marker(data, group_name, group_name, color)
            if marker:
                markers.append(marker)
        return markers

    def extract_single_marker(self, obj, identifier, group="default", color="red"):
        """Extract a single marker from an object."""
        if not isinstance(obj, dict):
            return None
            
        # Look for geometry field first
        if "geometry" in obj and isinstance(obj["geometry"], dict):
            geometry = obj["geometry"]
            if "latitude" in geometry and "longitude" in geometry:
                try:
                    lat = float(geometry["latitude"])
                    lng = float(geometry["longitude"])
                    
                    # Create popup text with available info
                    popup_parts = []
                    if group != "default":
                        popup_parts.append(f"Type: {group}")
                    if "location" in obj and obj["location"]:
                        popup_parts.append(f"Location: {obj['location']}")
                    if "start" in obj and obj["start"]:
                        popup_parts.append(f"Start: {obj['start']}")
                    if "end" in obj and obj["end"]:
                        popup_parts.append(f"End: {obj['end']}")
                    
                    popup_text = " | ".join(popup_parts) if popup_parts else f"Point {identifier}"
                    
                    return {
                        "latitude": lat,
                        "longitude": lng,
                        "popup": popup_text,
                        "group": group,
                        "color": color
                    }
                except (ValueError, TypeError):
                    pass
        
        # Fallback to direct coordinate extraction
        lat, lng = self.extract_coordinates(obj)
        if lat is not None and lng is not None:
            return {
                "latitude": lat,
                "longitude": lng,
                "popup": f"Point {identifier}: {lat}, {lng}",
                "group": group,
                "color": color
            }
        
        return None
    
    def extract_coordinates(self, value):
        """Extract latitude and longitude from various input formats."""
        if isinstance(value, dict):
            # Handle geometry objects like from nodegoat
            if "latitude" in value and "longitude" in value:
                try:
                    return float(value["latitude"]), float(value["longitude"])
                except (ValueError, TypeError):
                    return None, None
            elif "coordinates" in value:
                coords = value["coordinates"]
                # Check if coordinates is a dict with lat/lon or latitude/longitude
                if isinstance(coords, dict):
                    try:
                        # Support lat/lon format
                        if "lat" in coords and "lon" in coords:
                            return float(coords["lat"]), float(coords["lon"])
                        # Support latitude/longitude format
                        elif "latitude" in coords and "longitude" in coords:
                            return float(coords["latitude"]), float(coords["longitude"])
                    except (ValueError, TypeError):
                        return None, None
                # Check if coordinates is a list (GeoJSON format)
                elif isinstance(coords, list) and len(coords) >= 2:
                    try:
                        # GeoJSON format: [longitude, latitude]
                        return float(coords[1]), float(coords[0])
                    except (ValueError, TypeError, IndexError):
                        return None, None
        elif isinstance(value, list) and len(value) >= 2:
            try:
                # Assume [latitude, longitude] or [longitude, latitude]
                # Try both orders and use the one that makes geographic sense
                lat1, lon1 = float(value[0]), float(value[1])
                lat2, lon2 = float(value[1]), float(value[0])
                
                # Check which interpretation makes more geographic sense
                if -90 <= lat1 <= 90 and -180 <= lon1 <= 180:
                    return lat1, lon1
                elif -90 <= lat2 <= 90 and -180 <= lon2 <= 180:
                    return lat2, lon2
                else:
                    return lat1, lon1  # Fallback to first interpretation
            except (ValueError, TypeError, IndexError):
                return None, None
        elif isinstance(value, str):
            # Try to parse coordinate strings like "47.5537, 8.0219"
            try:
                parts = value.replace(" ", "").split(",")
                if len(parts) == 2:
                    return float(parts[0]), float(parts[1])
            except (ValueError, IndexError):
                pass
        
        return None, None



class TextTruncateFilter(AbstractFilter):
    """A filter to truncate long text with optional expandable functionality."""

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["length", "expandable", "expand_text", "collapse_text", "ellipsis"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns truncated text with optional expand/collapse functionality."""
        import uuid
        import html

        value = self.get_value()
        if not value:
            return ""

        text = str(value).strip()
        if not text:
            return ""

        # Configuration
        max_length = int(self.get_configuration("length") or 200)
        is_expandable = self.get_configuration("expandable") != "false"  # Default to true
        expand_text = self.get_configuration("expand_text") or "Show more"
        collapse_text = self.get_configuration("collapse_text") or "Show less"
        ellipsis = self.get_configuration("ellipsis") or "..."

        # If text is short enough, return as-is
        if len(text) <= max_length:
            return f"<span>{html.escape(text)}</span>"

        # Truncate text at word boundary if possible
        truncated = text[:max_length]
        if " " in text[max_length:max_length+20]:  # Look ahead for word boundary
            last_space = truncated.rfind(" ")
            if last_space > max_length * 0.8:  # Only use word boundary if not too far back
                truncated = truncated[:last_space]

        # Escape HTML in text
        truncated_escaped = html.escape(truncated)
        full_text_escaped = html.escape(text)

        if not is_expandable:
            # Non-expandable: just return truncated text with ellipsis
            return f"<span>{truncated_escaped}{ellipsis}</span>"

        # Expandable: create interactive version
        unique_id = f"text_{uuid.uuid4().hex[:8]}"

        return f"""
        <span id="{unique_id}_container">
            <span id="{unique_id}_truncated">{truncated_escaped}{ellipsis}
                <a href="#" id="{unique_id}_expand" style="color: #007bff; text-decoration: none; font-size: 0.9em; cursor: pointer;">{expand_text}</a>
            </span>
            <span id="{unique_id}_full" style="display: none;">{full_text_escaped}
                <a href="#" id="{unique_id}_collapse" style="color: #007bff; text-decoration: none; font-size: 0.9em; cursor: pointer;">{collapse_text}</a>
            </span>
        </span>
        <script>
        (function() {{
            var expandBtn = document.getElementById("{unique_id}_expand");
            var collapseBtn = document.getElementById("{unique_id}_collapse");
            var truncatedSpan = document.getElementById("{unique_id}_truncated");
            var fullSpan = document.getElementById("{unique_id}_full");

            if (expandBtn) {{
                expandBtn.addEventListener("click", function(e) {{
                    e.preventDefault();
                    truncatedSpan.style.display = "none";
                    fullSpan.style.display = "inline";
                }});
            }}

            if (collapseBtn) {{
                collapseBtn.addEventListener("click", function(e) {{
                    e.preventDefault();
                    fullSpan.style.display = "none";
                    truncatedSpan.style.display = "inline";
                }});
            }}
        }})();
        </script>
        """


class ReadableNumberFilter(AbstractFilter):
    """A filter to format numbers with separators for better readability.

    Usage: [number|readable(separator="'")]
    Examples:
        123456 -> 123'456
        1234567890 -> 1'234'567'890
        With separator=",": 123456 -> 123,456
    """

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["separator"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns the formatted number with separators."""
        try:
            value = self.get_value()
            separator = self.get_configuration("separator") or "'"

            # Convert to int/float if it's a string
            if isinstance(value, str):
                value = float(value) if '.' in value else int(value)

            # Split into integer and decimal parts
            if isinstance(value, float):
                int_part, dec_part = str(value).split('.')
                formatted_int = "{:,}".format(int(int_part)).replace(',', separator)
                return f"{formatted_int}.{dec_part}"
            else:
                return "{:,}".format(int(value)).replace(',', separator)
        except (ValueError, TypeError, AttributeError):
            return self.get_value()


class CompactNumberFilter(AbstractFilter):
    """A filter to format numbers in compact form (K for thousands, M for millions).

    Usage: [number|compact(precision="1")]
    Examples:
        21438 -> 21.4K
        1234567 -> 1.2M
        123 -> 123
        With precision=0: 21438 -> 21K
    """

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["precision"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns the formatted number in compact form."""
        try:
            value = self.get_value()
            precision = int(self.get_configuration("precision") or 1)

            # Convert to number if it's a string
            if isinstance(value, str):
                value = float(value) if '.' in value else int(value)

            num = float(value)

            if abs(num) >= 1_000_000_000:
                formatted = f"{num / 1_000_000_000:.{precision}f}B"
            elif abs(num) >= 1_000_000:
                formatted = f"{num / 1_000_000:.{precision}f}M"
            elif abs(num) >= 1_000:
                formatted = f"{num / 1_000:.{precision}f}K"
            else:
                return str(int(num) if num == int(num) else num)

            # Remove trailing zeros after decimal point
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')

            return formatted
        except (ValueError, TypeError, AttributeError):
            return self.get_value()


class RelativeDateFilter(AbstractFilter):
    """A filter to format dates as relative time (e.g., 'today', 'yesterday', '2 days ago').

    Usage: [date|relative()]
    Examples:
        Today's date -> "today"
        Yesterday -> "yesterday"
        2 days ago -> "2 days ago"
        Last week -> "1 week ago"
        Older dates -> formatted as "13.10.2025"
    """

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["format"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns the date formatted as relative time."""
        from django.utils import timezone

        try:
            value = self.get_value()

            # Parse the date if it's a string
            if isinstance(value, str):
                # Try common date formats
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d.%m.%Y", "%d/%m/%Y", "%m/%d/%Y"]:
                    try:
                        date_obj = datetime.strptime(value, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    return self.get_value()  # If no format matches, return original
            elif isinstance(value, datetime):
                date_obj = value.date()
            elif hasattr(value, 'year'):  # date object
                date_obj = value
            else:
                return self.get_value()

            # Get today's date (timezone-aware if needed)
            today = timezone.now().date() if timezone.is_aware(timezone.now()) else datetime.now().date()

            # Calculate difference
            diff = (today - date_obj).days

            if diff == 0:
                return "today"
            elif diff == 1:
                return "yesterday"
            elif diff == -1:
                return "tomorrow"
            elif diff > 1 and diff < 7:
                return f"{diff} days ago"
            elif diff == 7:
                return "1 week ago"
            elif diff > 7 and diff < 30:
                weeks = diff // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            elif diff >= 30 and diff < 365:
                months = diff // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            elif diff >= 365:
                years = diff // 365
                return f"{years} year{'s' if years > 1 else ''} ago"
            elif diff < -1 and diff > -7:
                return f"in {abs(diff)} days"
            elif diff <= -7 and diff > -30:
                weeks = abs(diff) // 7
                return f"in {weeks} week{'s' if weeks > 1 else ''}"
            else:
                # For older dates or far future dates, return formatted date
                format_str = self.get_configuration("format") or "%d.%m.%Y"
                return date_obj.strftime(format_str)
        except (ValueError, TypeError, AttributeError):
            return self.get_value()


class TableTemplateFilter(AbstractFilter):
    """A filter to render list data as an HTML table with column configuration and filter expressions.

    Usage:
        {data|table}  # Simple table with auto-detected columns
        {contributors|table:cols=[role,contributors],headers=[Role,Contributors],expr=["capitalize","badge:field=person"],tstyle=striped}

    Configuration:
        - cols: Array of column keys to display (supports dot-notation for nested values)
        - headers: Array of header labels (default: capitalize column keys)
        - expr: Array of filter expressions to apply to each column
        - tstyle: Table style (plain, small, striped, small-striped, bordered, hover, sm-striped)
        - tclass: Additional CSS classes for the table
        - rowclass: CSS class for table rows
        - limit: Maximum number of rows to display
        - empty: Text to display when list is empty (default: "No data available")
        - empty_cell: Text to display for empty/missing cells (default: "&nbsp;" - non-breaking space)
        - join: Separator when cell contains a list (default: ", ")
        - responsive: Whether to wrap in responsive div (default: true)
    """

    STYLE_CLASSES = {
        'plain': 'table',
        'small': 'table table-sm',
        'sm': 'table table-sm',
        'striped': 'table table-striped',
        'small-striped': 'table table-sm table-striped',
        'sm-striped': 'table table-sm table-striped',
        'bordered': 'table table-bordered',
        'hover': 'table table-hover',
    }

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["cols", "headers", "expr", "widths", "tstyle", "tclass", "rowclass",
                "limit", "empty", "empty_cell", "join", "responsive"]

    def needed_options(self):
        return []

    def processes_list_as_whole(self):
        """This filter needs to process the entire list at once."""
        return True

    def get_rendered_value(self):
        """Returns the formatted table HTML."""
        value = self.value

        # Validate input is a list
        if not isinstance(value, list):
            return f"<span class='text-danger'>Table filter requires a list, got {type(value).__name__}</span>"

        if len(value) == 0:
            empty_message = self.get_configuration("empty") or "No data available"
            return f"<div class='text-muted'>{empty_message}</div>"

        # Parse configurations
        cols = self.parse_array_config(self.get_configuration("cols"))
        headers = self.parse_array_config(self.get_configuration("headers"))
        expressions = self.parse_array_config(self.get_configuration("expr"), preserve_quotes=True, delimiter=';')
        widths = self.parse_array_config(self.get_configuration("widths"), delimiter=';')

        # Auto-detect columns if not specified
        if not cols:
            cols = self.auto_detect_columns(value)

        # Auto-generate headers if not specified
        if not headers:
            headers = [self.format_header(col) for col in cols]

        # Validate headers match columns
        if len(headers) != len(cols):
            return f"<span class='text-danger'>Headers count ({len(headers)}) must match columns count ({len(cols)})</span>"

        # Validate expressions match columns (if provided)
        if expressions and len(expressions) != len(cols):
            return f"<span class='text-danger'>Expressions count ({len(expressions)}) must match columns count ({len(cols)})</span>"

        # Apply row limit if specified
        limit = self.get_configuration("limit")
        if limit:
            try:
                value = value[:int(limit)]
            except (ValueError, TypeError):
                pass

        # Build table HTML
        table_html = self.build_table_html(value, cols, headers, expressions, widths)

        # Wrap in responsive div if configured
        responsive = self.get_configuration("responsive")
        if responsive is None or responsive.lower() not in ["false", "0", "no"]:
            table_html = f'<div class="table-responsive">{table_html}</div>'

        return table_html

    def build_table_html(self, data, cols, headers, expressions, widths=None):
        """Build the complete table HTML."""
        # Determine table classes
        tstyle = self.get_configuration("tstyle") or "plain"
        table_classes = self.STYLE_CLASSES.get(tstyle, "table")

        # Add additional classes if specified
        tclass = self.get_configuration("tclass")
        if tclass:
            table_classes += f" {tclass}"

        # Build table
        table = HTMLElement("table")
        table.add_attribute("class", table_classes)

        # Emit <colgroup> if widths were specified
        if widths:
            colgroup_html = '<colgroup>'
            for i in range(len(cols)):
                w = widths[i] if i < len(widths) else ''
                if w:
                    colgroup_html += f'<col style="width:{w}">'
                else:
                    colgroup_html += '<col>'
            colgroup_html += '</colgroup>'
            table.add_content(colgroup_html)

        # Build thead
        thead = HTMLElement("thead")
        thead_row = HTMLElement("tr")
        for header in headers:
            th = HTMLElement("th")
            th.add_content(header)
            thead_row.add_content(str(th))
        thead.add_content(str(thead_row))
        table.add_content(str(thead))

        # Build tbody
        tbody = HTMLElement("tbody")
        rowclass = self.get_configuration("rowclass")

        # Get empty cell default once
        empty_default = self.get_configuration("empty_cell")
        if empty_default is None:
            empty_default = "&nbsp;"

        for row_idx, row_data in enumerate(data):
            # Build all cells first into a list
            cells = []

            for i in range(len(cols)):
                col = cols[i]
                cell_html = "<td>&nbsp;</td>"  # Default empty cell

                try:
                    # Extract cell value (with nested support)
                    cell_value = self.extract_cell_value(row_data, col)

                    # Apply filter expression if specified
                    if expressions and i < len(expressions) and expressions[i]:
                        try:
                            cell_value = self.apply_filter_expression(cell_value, expressions[i], row_data)
                        except Exception:
                            cell_value = None

                    # Handle lists within cells
                    if isinstance(cell_value, list):
                        join_separator = self.get_configuration("join") or ", "
                        cell_value = join_separator.join(str(item) for item in cell_value if item is not None)

                    # Handle None/empty values
                    if cell_value is None or cell_value == "":
                        cell_value = empty_default

                    # Build cell HTML
                    td = HTMLElement("td")
                    td.add_content(str(cell_value))
                    cell_html = str(td)

                except Exception:
                    # Any error: use default empty cell
                    cell_html = f"<td>{empty_default}</td>"

                # Add to cells list - GUARANTEED
                cells.append(cell_html)

            # Verify we have exactly the right number of cells
            while len(cells) < len(cols):
                cells.append(f"<td>{empty_default}</td>")

            # Build row with all cells
            tr = HTMLElement("tr")
            if rowclass:
                tr.add_attribute("class", rowclass)

            for cell_html in cells:
                tr.add_content(cell_html)

            row_html = str(tr)
            tbody.add_content(row_html)

        table.add_content(str(tbody))

        return str(table)

    def extract_cell_value(self, row_data, col_key):
        """Extract a cell value from row data, supporting dot-notation for nested values."""
        if not isinstance(row_data, dict):
            return row_data

        # Handle dot-notation for nested values
        if '.' in col_key:
            return get_nested_value(row_data, col_key)

        # Simple key access
        return row_data.get(col_key, None)

    def apply_filter_expression(self, value, expr_str, row_data):
        """Apply a filter expression string to a value. Supports chained filters with |.

        Args:
            value: The value to filter
            expr_str: Filter expression like "upper" or "format:.2f|badge:bg=gradient"
            row_data: The full row data for context

        Returns:
            Filtered value
        """
        if not expr_str:
            return value

        # Remove surrounding quotes if present
        expr_str = self.remove_quotes(expr_str)

        # Split by pipe to support chained filters
        filter_chain = self.split_filter_chain(expr_str)

        # Handle lists - apply filter chain to each item
        if isinstance(value, list):
            filtered_items = []
            for item in value:
                try:
                    filtered = item
                    # Apply each filter in the chain
                    for filter_expr in filter_chain:
                        filtered = self.apply_single_filter_expression(filtered, filter_expr, row_data)
                    if filtered is not None:
                        filtered_items.append(filtered)
                except Exception:
                    # If filter fails, keep original item
                    if item is not None:
                        filtered_items.append(item)
            return filtered_items

        # Apply filter chain to single value
        try:
            filtered_value = value
            for filter_expr in filter_chain:
                filtered_value = self.apply_single_filter_expression(filtered_value, filter_expr, row_data)
            return filtered_value
        except Exception:
            # If filter fails, return original value
            return value

    def split_filter_chain(self, expr_str):
        """Split a filter expression into a chain by '|', respecting quotes.

        Example: "format:.2f|badge:bg=gradient" -> ["format:.2f", "badge:bg=gradient"]
        """
        chain = []
        current = ""
        in_quotes = False
        quote_char = None

        for i, char in enumerate(expr_str):
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current += char
            elif char == quote_char and in_quotes:
                if i > 0 and expr_str[i - 1] == '\\':
                    current += char
                else:
                    in_quotes = False
                    quote_char = None
                    current += char
            elif char == '|' and not in_quotes:
                if current.strip():
                    chain.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            chain.append(current.strip())

        return chain if chain else [expr_str]

    def apply_single_filter_expression(self, value, expr_str, row_data):
        """Apply filter expression to a single value."""
        # Parse the filter expression
        # Format: "filter_name" or "filter_name:param=value,param2=value2"
        if ':' in expr_str:
            filter_name, config_str = expr_str.split(':', 1)
        else:
            filter_name = expr_str
            config_str = ""

        # Parse configuration
        filter_config = {}
        if config_str:
            # Split by comma, respecting quotes
            configs = self.split_respecting_quotes(config_str, ',')
            for config in configs:
                if '=' in config:
                    k, v = config.split('=', 1)
                    filter_config[k.strip()] = self.remove_quotes(v.strip())
                else:
                    # Positional parameter
                    filter_config[f"o{len(filter_config)}"] = self.remove_quotes(config.strip())

        # Get filter class and apply
        try:
            filter_class = get_get_filter_class(filter_name.strip())
            return filter_class(filter_name.strip(), value, filter_config, row_data).get_rendered_value()
        except ValueError:
            # Filter not found, return value as-is
            return value

    def parse_array_config(self, config_str, preserve_quotes=False, delimiter=','):
        """Parse array configuration like [item1,item2,item3] into a list.

        Args:
            config_str: Configuration string
            preserve_quotes: If True, keep quotes around items (useful for filter expressions)
            delimiter: Character to use for splitting array elements (default ',', use ';' for expr arrays)

        Returns:
            List of items
        """
        if not config_str:
            return []

        config_str = config_str.strip()

        # Remove outer brackets
        if config_str.startswith('[') and config_str.endswith(']'):
            config_str = config_str[1:-1]

        if not config_str:
            return []

        # Split by delimiter, respecting quotes
        items = self.split_respecting_quotes(config_str, delimiter)

        # Clean up items
        result = []
        for item in items:
            item = item.strip()
            if not preserve_quotes:
                item = self.remove_quotes(item)
            result.append(item)

        return result

    def split_respecting_quotes(self, text, delimiter):
        """Split text by delimiter, but respect quoted strings."""
        parts = []
        current_part = ""
        in_quotes = False
        quote_char = None

        for i, char in enumerate(text):
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_part += char
            elif char == quote_char and in_quotes:
                # Check if it's escaped
                if i > 0 and text[i - 1] == '\\':
                    current_part += char
                else:
                    in_quotes = False
                    quote_char = None
                    current_part += char
            elif char == delimiter and not in_quotes:
                if current_part.strip():
                    parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char

        if current_part.strip():
            parts.append(current_part.strip())

        return parts

    def remove_quotes(self, text):
        """Remove surrounding quotes from text."""
        text = text.strip()
        if len(text) >= 2:
            if (text.startswith('"') and text.endswith('"')) or \
                    (text.startswith("'") and text.endswith("'")):
                return text[1:-1]
        return text

    def auto_detect_columns(self, data):
        """Auto-detect columns from the first item in the list."""
        if not data or len(data) == 0:
            return []

        first_item = data[0]
        if isinstance(first_item, dict):
            return list(first_item.keys())

        return []

    def format_header(self, col_key):
        """Format a column key into a readable header.

        Examples:
            'role' -> 'Role'
            'first_name' -> 'First Name'
            'user.name' -> 'User Name'
        """
        # Handle dot-notation
        if '.' in col_key:
            col_key = col_key.split('.')[-1]

        # Replace underscores with spaces and capitalize
        return col_key.replace('_', ' ').title()


class DatatableFilter(TableTemplateFilter):
    """A filter to render interactive data tables using Tabulator.

    This extends TableTemplateFilter to provide pagination, filtering, and sorting capabilities.

    Usage:
        {data|datatable}  # Basic interactive table
        {data|datatable:cols=[name,age],headers=[Name,Age],pagesize=10}
        {data|datatable:filterable=true,sortable=true,paginate=true}
        {data|datatable:cols=[role,name],expr=["capitalize","badge:field=person"]}

    Configuration (inherits all from table filter):
        - cols: Array of column keys to display
        - headers: Array of header labels
        - expr: Array of filter expressions for each column
        - limit: Maximum rows (if not paginating)
        - empty: Empty state message
        - empty_cell: Default for empty cells
        - join: List separator

    Datatable-specific options:
        - paginate: Enable pagination (true/false, default: true)
        - pagesize: Rows per page (default: 10, options: 5,10,25,50,100)
        - filterable: Enable column filtering (true/false, default: true)
        - sortable: Enable column sorting (true/false, default: true)
        - height: Table height (e.g., "400px", default: auto)
        - layout: Layout mode ("fitData", "fitColumns", "fitDataFill", default: "fitData")
        - responsive: Enable responsive layout (true/false, default: true)
    """

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        # Extend parent's allowed attributes
        parent_attrs = super().allowed_attributes()
        datatable_attrs = ["paginate", "pagesize", "filterable", "sortable",
                          "height", "layout", "responsive"]
        return parent_attrs + datatable_attrs

    def needed_options(self):
        return []

    def processes_list_as_whole(self):
        """This filter needs to process the entire list at once."""
        return True

    def get_rendered_value(self):
        """Returns the Tabulator table HTML and JavaScript."""
        value = self.value

        # Debug output
        print(f"[DATATABLE DEBUG] Filter called with value type: {type(value)}")
        print(f"[DATATABLE DEBUG] Value is list: {isinstance(value, list)}")
        if isinstance(value, list):
            print(f"[DATATABLE DEBUG] List length: {len(value)}")

        # Validate input
        if not isinstance(value, list):
            error_msg = f"<div class='alert alert-danger'>Datatable filter requires a list, got {type(value).__name__}. Value: {str(value)[:100]}</div>"
            print(f"[DATATABLE DEBUG] Returning error: {error_msg}")
            return error_msg

        if len(value) == 0:
            empty_message = self.get_configuration("empty") or "No data available"
            print(f"[DATATABLE DEBUG] Empty list, returning: {empty_message}")
            return f"<div class='text-muted'>{empty_message}</div>"

        # Parse configurations
        cols = self.parse_array_config(self.get_configuration("cols"))
        headers = self.parse_array_config(self.get_configuration("headers"))
        expressions = self.parse_array_config(self.get_configuration("expr"), preserve_quotes=True, delimiter=';')

        # Auto-detect columns if not specified
        if not cols:
            cols = self.auto_detect_columns(value)

        # Auto-generate headers if not specified
        if not headers:
            headers = [self.format_header(col) for col in cols]

        # Validate
        if len(headers) != len(cols):
            return f"<span class='text-danger'>Headers count ({len(headers)}) must match columns count ({len(cols)})</span>"

        if expressions and len(expressions) != len(cols):
            return f"<span class='text-danger'>Expressions count ({len(expressions)}) must match columns count ({len(cols)})</span>"

        # Get datatable-specific options
        paginate = self.get_configuration("paginate")
        paginate = paginate is None or paginate.lower() not in ["false", "0", "no"]

        pagesize = int(self.get_configuration("pagesize") or 10)
        filterable = self.get_configuration("filterable")
        filterable = filterable is None or filterable.lower() not in ["false", "0", "no"]

        sortable = self.get_configuration("sortable")
        sortable = sortable is None or sortable.lower() not in ["false", "0", "no"]

        height = self.get_configuration("height") or None
        layout = self.get_configuration("layout") or "fitColumns"

        responsive = self.get_configuration("responsive")
        responsive = responsive is None or responsive.lower() not in ["false", "0", "no"]

        # Process data - apply expressions to create clean data for Tabulator
        print(f"[DATATABLE DEBUG] Processing data with {len(cols)} columns")
        processed_data = self.process_data_for_tabulator(value, cols, expressions)
        print(f"[DATATABLE DEBUG] Processed {len(processed_data)} rows")

        # Build the Tabulator HTML and JS
        print(f"[DATATABLE DEBUG] Building Tabulator table")
        result = self.build_tabulator_table(processed_data, cols, headers, {
            'paginate': paginate,
            'pagesize': pagesize,
            'filterable': filterable,
            'sortable': sortable,
            'height': height,
            'layout': layout,
            'responsive': responsive
        })
        print(f"[DATATABLE DEBUG] Returning result length: {len(result)}")
        return result

    def process_data_for_tabulator(self, data, cols, expressions):
        """Process data and apply filter expressions to create Tabulator-ready data."""
        processed = []
        empty_default = self.get_configuration("empty_cell") or ""

        for row_data in data:
            row = {}
            for i, col in enumerate(cols):
                try:
                    # Extract cell value
                    cell_value = self.extract_cell_value(row_data, col)

                    # Apply filter expression if specified
                    if expressions and i < len(expressions) and expressions[i]:
                        try:
                            cell_value = self.apply_filter_expression(cell_value, expressions[i], row_data)
                        except Exception:
                            cell_value = None

                    # Handle lists within cells
                    if isinstance(cell_value, list):
                        join_separator = self.get_configuration("join") or ", "
                        cell_value = join_separator.join(str(item) for item in cell_value if item is not None)

                    # Handle None/empty values
                    if cell_value is None or cell_value == "":
                        cell_value = empty_default

                    row[col] = str(cell_value)
                except Exception:
                    row[col] = empty_default

            processed.append(row)

        return processed

    def build_tabulator_table(self, data, cols, headers, options):
        """Build the Tabulator table HTML and JavaScript."""
        import json
        import html as html_module

        # Generate unique IDs
        table_id = f"datatable-{uuid.uuid4().hex[:8]}"
        # Function names can't have dashes in JavaScript, so create a sanitized version
        func_id = table_id.replace('-', '_')

        # Build column definitions
        columns = []
        for i, col in enumerate(cols):
            column_def = {
                'title': headers[i],
                'field': col,
                'headerFilter': options['filterable'],
                'headerSort': options['sortable'],
                'formatter': 'html',  # Allow HTML rendering in cells (for badges, links, etc.)
                'responsive': 0 if i == 0 else None  # First column always visible in responsive mode
            }
            columns.append(column_def)

        # Serialize data and columns - use ensure_ascii to prevent encoding issues
        data_json = json.dumps(data, ensure_ascii=True)
        columns_json = json.dumps(columns, ensure_ascii=True)

        # Build container
        container_style = ""
        if options['height']:
            container_style = f"height: {options['height']};"

        # Store JSON data in hidden script tags to avoid escaping issues
        data_script_id = f"{table_id}-data"
        columns_script_id = f"{table_id}-columns"

        html = f'''<div id="{table_id}" style="{container_style}"></div>
        <script type="application/json" id="{data_script_id}">{data_json}</script>
        <script type="application/json" id="{columns_script_id}">{columns_json}</script>'''

        # Build JavaScript
        pagination_config = "true" if options['paginate'] else "false"
        pagination_size = options['pagesize']

        # Resolve static file URLs using Django's static template tag
        tabulator_css_url = static('ndr_core/plugins/tabulator/css/tabulator.min.css')
        tabulator_js_url = static('ndr_core/plugins/tabulator/js/tabulator.min.js')

        script = f"""
        <script>
            (function() {{
                // Ensure Tabulator CSS is loaded
                if (!document.querySelector('link[href*="tabulator"]')) {{
                    var link = document.createElement('link');
                    link.rel = 'stylesheet';
                    link.href = '{tabulator_css_url}';
                    document.head.appendChild(link);
                }}

                // Ensure Tabulator JS is loaded
                if (typeof Tabulator === 'undefined') {{
                    var script = document.createElement('script');
                    script.src = '{tabulator_js_url}';
                    script.onload = function() {{ initTable_{func_id}(); }};
                    document.head.appendChild(script);
                }} else {{
                    initTable_{func_id}();
                }}

                function initTable_{func_id}() {{
                    // Parse data from JSON script tags
                    var data = JSON.parse(document.getElementById('{data_script_id}').textContent);
                    var columns = JSON.parse(document.getElementById('{columns_script_id}').textContent);

                    // Check current theme
                    var isDark = document.documentElement.getAttribute('data-theme') === 'dark';

                    var table = new Tabulator("#{table_id}", {{
                        data: data,
                        columns: columns,
                        layout: "{options['layout']}",
                        pagination: {pagination_config},
                        paginationSize: {pagination_size},
                        paginationSizeSelector: [5, 10, 25, 50, 100],
                        responsiveLayout: {str(options['responsive']).lower()},
                        responsiveLayoutCollapseStartOpen: false,
                        headerFilterPlaceholder: "Filter...",
                        renderComplete: function() {{
                            applyTheme_{func_id}();
                            // Force redraw after a short delay to ensure proper column sizing
                            setTimeout(function() {{
                                table.redraw(true);
                            }}, 10);
                        }}
                    }});

                    function applyTheme_{func_id}() {{
                        var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
                        var container = document.getElementById('{table_id}');

                        if (isDark) {{
                            container.classList.add('tabulator-dark');
                            container.classList.remove('tabulator-light');
                        }} else {{
                            container.classList.add('tabulator-light');
                            container.classList.remove('tabulator-dark');
                        }}
                    }}

                    // Apply initial theme
                    applyTheme_{func_id}();

                    // Watch for theme changes
                    var observer = new MutationObserver(function(mutations) {{
                        mutations.forEach(function(mutation) {{
                            if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {{
                                applyTheme_{func_id}();
                            }}
                        }});
                    }});

                    observer.observe(document.documentElement, {{
                        attributes: true,
                        attributeFilter: ['data-theme']
                    }});
                }}
            }})();
        </script>
        """

        return html + script


class CodeFilter(AbstractFilter):
    """A filter to render code blocks with optional syntax highlighting.

    Usage:
        {code_string|code}  # Basic code block
        {json_data|code:lang=json}  # JSON with language hint
        {python_code|code:lang=python,linenumbers=true}  # Python with line numbers
        {data|code:lang=json,pretty=true}  # Pretty-print JSON
        {long_code|code:maxheight=300px}  # Limit height with scrolling
        {text_with_escapes|code:nl2br=true}  # Convert \n to actual line breaks

    Configuration:
        - lang: Language for syntax highlighting (python, json, javascript, html, css, etc.)
        - linenumbers: Show line numbers (true/false, default: false)
        - class: Additional CSS classes for the code block
        - style: Inline CSS styles
        - pretty: Pretty-print JSON data (true/false, default: true for JSON)
        - indent: Indentation spaces for pretty-printing (default: 2)
        - wrap: Enable word wrapping (true/false, default: false)
        - maxheight: Maximum height with scrolling (e.g., 300px, 20rem)
        - nl2br: Convert literal \n escape sequences to actual newlines (true/false, default: false)
    """

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["lang", "linenumbers", "class", "style", "pretty", "indent", "wrap", "maxheight", "nl2br"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns the code block HTML."""
        import html

        value = self.get_value()

        if value is None or value == "":
            return ""

        # Get configuration
        lang = self.get_configuration("lang") or ""
        show_linenumbers = self.get_configuration("linenumbers") == "true"
        custom_class = self.get_configuration("class") or ""
        custom_style = self.get_configuration("style") or ""
        pretty = self.get_configuration("pretty")
        indent = int(self.get_configuration("indent") or 2)
        wrap = self.get_configuration("wrap") == "true"
        maxheight = self.get_configuration("maxheight")
        nl2br = self.get_configuration("nl2br") == "true"

        # Convert value to string and handle JSON pretty-printing
        code_content = self.format_code_content(value, lang, pretty, indent)

        # Convert literal \n to actual newlines if nl2br is enabled
        if nl2br and isinstance(code_content, str):
            code_content = code_content.replace('\\n', '\n').replace('\\r\\n', '\n').replace('\\r', '\n')

        # Escape HTML
        code_content = html.escape(code_content)

        # Build CSS classes
        css_classes = ["code-block"]
        if lang:
            css_classes.append(f"language-{lang}")
        if custom_class:
            css_classes.extend(custom_class.split())

        # Build inline styles
        styles = []
        styles.append("font-size: 0.7rem")  # Smaller text (14px on most browsers)
        if not wrap:
            styles.append("white-space: pre")
            styles.append("overflow-x: auto")
        else:
            styles.append("white-space: pre-wrap")

        # Add max-height and scrolling if configured
        if maxheight:
            styles.append(f"max-height: {maxheight}")
            styles.append("overflow-y: auto")

        if custom_style:
            styles.append(custom_style)

        style_attr = "; ".join(styles)

        # Build the HTML
        pre_element = HTMLElement("pre")
        pre_element.add_attribute("class", " ".join(css_classes))
        if style_attr:
            pre_element.add_attribute("style", style_attr)

        code_element = HTMLElement("code")
        if lang:
            code_element.add_attribute("class", f"language-{lang}")

        # Add line numbers if requested
        if show_linenumbers:
            code_content = self.add_line_numbers(code_content)
            code_element.add_attribute("style", "counter-reset: line")

        code_element.add_content(code_content)
        pre_element.add_content(str(code_element))

        return str(pre_element)

    def format_code_content(self, value, lang, pretty, indent):
        """Format the code content, with special handling for JSON."""
        # If it's a dict or list and language is JSON, serialize it
        if isinstance(value, (dict, list)):
            # Auto-detect JSON if not specified
            if not lang:
                lang = "json"

            # Determine if we should pretty-print
            should_pretty = pretty != "false" if pretty is not None else True

            if should_pretty:
                return json.dumps(value, indent=indent, ensure_ascii=False)
            else:
                return json.dumps(value, ensure_ascii=False)

        # For strings, check if they contain JSON and lang is json
        if isinstance(value, str) and lang == "json":
            should_pretty = pretty != "false" if pretty is not None else True

            if should_pretty:
                try:
                    # Try to parse and re-format as JSON
                    parsed = json.loads(value)
                    return json.dumps(parsed, indent=indent, ensure_ascii=False)
                except (json.JSONDecodeError, ValueError):
                    # If it's not valid JSON, return as-is
                    return value
            else:
                return value

        # For all other cases, return as string
        return str(value)

    def add_line_numbers(self, code_content):
        """Add line numbers to code content."""
        lines = code_content.split('\n')
        numbered_lines = []

        for i, line in enumerate(lines, 1):
            # Use CSS counters for line numbers
            numbered_lines.append(f'<span class="line-number" data-line="{i}"></span>{line}')

        return '\n'.join(numbered_lines)


class PlotlyFilter(AbstractFilter):
    """A filter to render Plotly interactive visualizations.

    Usage:
        {viz_data|plotly}  # Basic plotly chart
        {viz_data|plotly:height=400,width=600}  # Custom dimensions
        {viz_data|plotly:responsive=true}  # Responsive layout
        {viz_data|plotly:config=displayModeBar:false}  # Custom config

    The filter accepts either:
    - A dict with 'plotly_figure' key containing the figure data
    - A dict with 'data' and 'layout' keys (standard Plotly format)

    Configuration:
        - height: Chart height in pixels (default: 400)
        - width: Chart width in pixels or '100%' for responsive (default: 100%)
        - responsive: Enable responsive sizing (true/false, default: true)
        - displaylogo: Show Plotly logo (true/false, default: false)
        - displaymodebar: Show mode bar (true/false, default: true)
        - staticplot: Make plot static (no interactions) (true/false, default: false)

    Note: Requires Plotly.js to be loaded on the page. Add to your base template:
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    """

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["height", "width", "responsive", "displaylogo", "displaymodebar", "staticplot", "config"]

    def needed_options(self):
        return []

    def get_rendered_value(self):
        """Returns the Plotly visualization HTML."""
        value = self.get_value()

        if value is None or value == "":
            return ""

        # Extract plotly figure data
        figure_data = self.extract_figure_data(value)

        if not figure_data:
            return '<div class="alert alert-warning">Invalid Plotly data format</div>'

        # Get configuration
        height = self.get_configuration("height") or "400"
        width = self.get_configuration("width") or "100%"
        responsive = self.get_configuration("responsive") != "false"  # Default true
        displaylogo = self.get_configuration("displaylogo") == "true"  # Default false
        displaymodebar = self.get_configuration("displaymodebar") != "false"  # Default true
        staticplot = self.get_configuration("staticplot") == "true"  # Default false

        # Generate unique ID for the div
        chart_id = f"plotly-{uuid.uuid4().hex[:8]}"

        # Build Plotly config
        config = {
            "displaylogo": displaylogo,
            "displayModeBar": displaymodebar,
            "staticPlot": staticplot,
            "responsive": responsive
        }

        # Serialize figure data and config to JSON
        try:
            figure_json = json.dumps(figure_data, ensure_ascii=False)
            config_json = json.dumps(config, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            return f'<div class="alert alert-danger">Error serializing Plotly data: {e}</div>'

        # Build the HTML
        container_div = HTMLElement("div")
        container_div.add_attribute("id", chart_id)
        container_div.add_attribute("style", f"width: {width}; height: {height}px;")

        # Build the script with dark mode support
        script = f"""
        <script>
            (function() {{
                var figureData = {figure_json};
                var config = {config_json};
                var isInitialized = false;

                // Function to get dark mode layout updates (only styling, no axis ranges)
                function getDarkModeLayoutUpdate() {{
                    return {{
                        paper_bgcolor: '#1E1E1E',
                        plot_bgcolor: '#1E1E1E',
                        'font.color': '#E9ECEF',
                        'xaxis.gridcolor': '#444',
                        'xaxis.zerolinecolor': '#666',
                        'xaxis.color': '#E9ECEF',
                        'yaxis.gridcolor': '#444',
                        'yaxis.zerolinecolor': '#666',
                        'yaxis.color': '#E9ECEF',
                        'legend.bgcolor': 'rgba(30, 30, 30, 0.8)',
                        'legend.bordercolor': '#666',
                        'legend.font.color': '#E9ECEF',
                        colorway: ['#00D4DF', '#00B0B9', '#DC3545', '#198754', '#0DCAF0', '#FFC107', '#E91E63', '#9C27B0']
                    }};
                }}

                function getLightModeLayoutUpdate() {{
                    return {{
                        paper_bgcolor: '#FFFFFF',
                        plot_bgcolor: '#FFFFFF',
                        'font.color': '#212529',
                        'xaxis.gridcolor': '#E1E1E1',
                        'xaxis.zerolinecolor': '#969696',
                        'xaxis.color': '#212529',
                        'yaxis.gridcolor': '#E1E1E1',
                        'yaxis.zerolinecolor': '#969696',
                        'yaxis.color': '#212529',
                        'legend.bgcolor': 'rgba(255, 255, 255, 0.9)',
                        'legend.bordercolor': '#CCCCCC',
                        'legend.font.color': '#212529',
                        colorway: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
                    }};
                }}

                // Function to apply theme
                function applyTheme() {{
                    var isDark = document.documentElement.getAttribute('data-theme') === 'dark';

                    if (!isInitialized) {{
                        // Initial render with theme
                        var layout = figureData.layout || {{}};

                        if (isDark) {{
                            var darkUpdate = getDarkModeLayoutUpdate();
                            // Deep merge for initial render
                            layout = Object.assign({{}}, layout);
                            layout.paper_bgcolor = darkUpdate.paper_bgcolor;
                            layout.plot_bgcolor = darkUpdate.plot_bgcolor;
                            if (!layout.font) layout.font = {{}};
                            layout.font.color = '#E9ECEF';
                            if (!layout.xaxis) layout.xaxis = {{}};
                            Object.assign(layout.xaxis, {{
                                gridcolor: '#444',
                                zerolinecolor: '#666',
                                color: '#E9ECEF'
                            }});
                            if (!layout.yaxis) layout.yaxis = {{}};
                            Object.assign(layout.yaxis, {{
                                gridcolor: '#444',
                                zerolinecolor: '#666',
                                color: '#E9ECEF'
                            }});
                            if (!layout.legend) layout.legend = {{}};
                            Object.assign(layout.legend, {{
                                bgcolor: 'rgba(30, 30, 30, 0.8)',
                                bordercolor: '#666',
                                font: {{ color: '#E9ECEF' }}
                            }});
                            layout.colorway = darkUpdate.colorway;
                        }}

                        Plotly.newPlot('{chart_id}', figureData.data, layout, config);
                        isInitialized = true;

                        // Force resize after a short delay to ensure proper sizing
                        setTimeout(function() {{
                            Plotly.Plots.resize('{chart_id}');
                        }}, 10);
                    }} else {{
                        // Use relayout to only update styling, preserving axis ranges
                        var update = isDark ? getDarkModeLayoutUpdate() : getLightModeLayoutUpdate();
                        Plotly.relayout('{chart_id}', update);
                    }}
                }}

                // Initial render
                applyTheme();

                // Watch for theme changes
                var observer = new MutationObserver(function(mutations) {{
                    mutations.forEach(function(mutation) {{
                        if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {{
                            applyTheme();
                        }}
                    }});
                }});

                observer.observe(document.documentElement, {{
                    attributes: true,
                    attributeFilter: ['data-theme']
                }});
            }})();
        </script>
        """

        return str(container_div) + script

    def extract_figure_data(self, value):
        """Extract Plotly figure data from various input formats.

        Accepts:
        - Dict with 'plotly_figure' key
        - Dict with 'data' and 'layout' keys
        - Dict that is the figure itself
        """
        if not isinstance(value, dict):
            return None

        # Check if value has 'plotly_figure' key
        if 'plotly_figure' in value:
            figure = value['plotly_figure']
            if isinstance(figure, dict) and 'data' in figure:
                return figure

        # Check if value itself is the figure (has 'data' key)
        if 'data' in value:
            return value

        return None


class BadgesFilter(AbstractFilter):
    """Renders a list of tag objects as colored, optionally linked Bootstrap badges.

    Each item in the list is expected to be a dict. Relevant fields are configurable.

    Params:
        text_field  — dict key for the badge label          (default: text)
        color_field — dict key whose value drives bg color  (default: type)
        id_field    — dict key for the link target id       (default: entry_id)
        label_field — dict key for the human-readable type  (default: label)
        param       — query-string parameter name for link  (default: id)
        page        — NDR page view_name; omit to skip link

    Tooltip format: "{color_field value}: {label_field value}"
    """

    def needed_attributes(self):
        return []

    def allowed_attributes(self):
        return ["text_field", "color_field", "id_field", "label_field", "param", "page", "tt"]

    def needed_options(self):
        return []

    def processes_list_as_whole(self):
        return True

    def get_rendered_value(self):
        items = self.value
        if not isinstance(items, list):
            items = [items]

        text_field = self.get_configuration("text_field") or "text"
        color_field = self.get_configuration("color_field") or "type"
        id_field = self.get_configuration("id_field") or "entry_id"
        label_field = self.get_configuration("label_field") or "label"
        param = self.get_configuration("param") or "id"
        page_name = self.get_configuration("page")

        page_url = None
        if page_name:
            try:
                page = NdrCorePage.objects.get(view_name=page_name)
                page_url = page.url()
            except NdrCorePage.DoesNotExist:
                pass

        badges_html = []
        for item in items:
            if not isinstance(item, dict):
                continue

            text_val = item.get(text_field, "")
            color_val = item.get(color_field, "")
            entry_id = item.get(id_field, "")
            label_val = item.get(label_field, "")

            bg_color = HTMLElement.get_color_from_value(color_val)
            # Auto-select dark/light text based on lightness (hsl lightness=80% is always dark enough)
            text_color = "#000000"

            tt_template = self.get_configuration("tt")
            if tt_template:
                tooltip = escape(re.sub(
                    r'\[([^\]]+)\]',
                    lambda m: str(item.get(m.group(1), '')),
                    tt_template
                ))
            elif color_val and label_val:
                tooltip = f"{escape(color_val)}: {escape(label_val)}"
            elif label_val:
                tooltip = escape(label_val)
            else:
                tooltip = ""

            badge_attrs = (
                f'class="badge badge-auto-text font-weight-normal" '
                f'style="background-color:{bg_color};color:{text_color};"'
            )
            if tooltip:
                badge_attrs += f' data-bs-toggle="tooltip" data-bs-placement="top" title="{tooltip}"'

            badge_html = f'<span {badge_attrs}>{escape(str(text_val))}</span>'

            if page_url and entry_id:
                badge_html = (
                    f'<a href="{escape(page_url)}?{escape(param)}={escape(str(entry_id))}" '
                    f'style="text-decoration:none;">{badge_html}</a>'
                )

            badges_html.append(badge_html)

        return mark_safe(
            '<span class="ndr-badges">' + " ".join(badges_html) + "</span>"
        )
