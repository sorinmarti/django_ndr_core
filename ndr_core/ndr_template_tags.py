"""NDR Core template tags."""
import re
import json
import html
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static

from ndr_core.exceptions import PreRenderError
from ndr_core.forms.forms_manifest import ManifestSelectionForm
from ndr_core.models import NdrCoreUIElement, NdrCoreImage, NdrCoreUpload, NdrCorePage
from ndr_core.ndr_templatetags.template_string import TemplateString
from ndr_core.api_factory import ApiFactory

class TextPreRenderer:
    """Class to pre-render text before it is displayed on the website."""

    MAX_ITERATIONS = 50
    ui_element_regex = r'\[\[element\|([a-zA-Z0-9_-]+)\]\]'
    link_element_regex = r'\[\[(file|page|orcid|plotly|link|image)(?:-([a-z]+)-([a-z0-9]+)(?:-([a-z0-9]+))?)?\|([0-9a-zA-Z_ /?=&;:.#%~+@-]*)(?:\|([^\]]*))?\]\]'
    url_element_regex = r'\[\[url\|([0-9a-zA-Z_ -]*)\]\]'  # deprecated, kept for parse-compat
    setting_regex = r'\[\[setting\|([a-zA-Z0-9_-]+)\]\]'
    # Updated regex to capture both old syntax ([[start_block=Title]]) and new syntax ([[start_block:options]])
    container_regex = r'\[\[(start|end)_(block|cell)(?:[:=](.*?))?\]\]'
    code_start_regex = r'\[\[start_code(?:=(.*?))?\]\]'
    code_end_regex = r'\[\[end_code\]\]'
    toc_regex = r'\[\[toc\]\]'
    float_regex = r'\[\[(float_right|float_left|float_text|end_float)\]\]'
    link_element_classes = {'image': NdrCoreImage, 'file': NdrCoreUpload, 'page': NdrCorePage, 'plotly': NdrCoreUpload}
    link_element_keys = {"page": "view_name"}

    text = None
    block_titles = None

    def __init__(self, text, request):
        self.text = text
        self.request = request
        self.block_titles = []

    def _parse_block_options(self, param_string):
        """Parse block options from the parameter string.

        Supports:
        - Old syntax: [[start_block=Title]] → title only
        - New syntax with options only: [[start_block:collapsible=true,back_to_top=true]]
        - New syntax with title + options: [[start_block=Title:collapsible=true]]
        - New syntax explicit: [[start_block:title=My Title,collapsible=true]]

        Returns dict with: {'title': str or None, 'collapsible': bool, 'back_to_top': bool}
        """
        options = {
            'title': None,
            'collapsible': False,
            'back_to_top': False
        }

        if not param_string:
            return options

        # Check if new syntax (contains comma or key=value pairs)
        if ',' in param_string or ('=' in param_string and ':' not in param_string and param_string.count('=') > 0):
            # New syntax with key=value pairs
            # Split by comma
            pairs = param_string.split(',')
            for pair in pairs:
                pair = pair.strip()
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if key == 'title':
                        options['title'] = value
                    elif key in ['collapsible', 'collapsable']:  # Support both spellings
                        options['collapsible'] = value.lower() in ['true', '1', 'yes']
                    elif key == 'back_to_top':
                        options['back_to_top'] = value.lower() in ['true', '1', 'yes']
        else:
            # Old syntax: just the title
            options['title'] = param_string

        return options

    def check_tags_integrity(self):
        """Checks if all tags are well-formed. """
        matches = re.finditer(self.container_regex, self.text)
        items = {}
        for match in matches:
            block_type = match.groups(0)[1]
            if block_type not in items:
                items[block_type] = {'start': 0, 'end': 0}
            if match.groups(0)[0] == "start":
                items[block_type]['start'] += 1
            if match.groups(0)[0] == "end":
                items[block_type]['end'] += 1

        for key, value in items.items():
            if value['start'] != value['end']:
                return False
        return True

    def create_containers(self):
        """Creates container elements (blocks and cells)."""
        if self.check_tags_integrity():
            rendered_text = self.text

            # First pass: Clean up CKEditor's paragraph wrappers around template tags
            rendered_text = self._clean_template_tag_wrappers(rendered_text)

            match = re.search(self.container_regex, rendered_text)
            security_breaker = 0
            block_counter = 0

            while match:
                full_match = match.group(0)
                action = match.group(1)  # 'start' or 'end'
                container_type = match.group(2)  # 'block' or 'cell'
                param = match.group(3) if len(match.groups()) >= 3 else None  # optional parameter

                if container_type == 'block':
                    # Block: parse options from param
                    if action == 'start':
                        block_counter += 1
                        options = self._parse_block_options(param)

                        # Generate unique ID for this block
                        if options['title']:
                            anchor_id = f"block-{block_counter}-{re.sub(r'[^a-z0-9]+', '-', options['title'].lower()).strip('-')}"
                            self.block_titles.append({'title': options['title'], 'anchor': anchor_id})
                        else:
                            anchor_id = f"block-{block_counter}"

                        # Start building the HTML
                        replacement_parts = []
                        replacement_parts.append(f'<div class="card mb-2 box-shadow" id="{anchor_id}">')

                        # Add card header if collapsible or has title
                        if options['collapsible'] or options['title']:
                            replacement_parts.append('<div class="card-header d-flex justify-content-between align-items-center">')

                            if options['collapsible']:
                                # Collapsible header with button
                                collapse_id = f"collapse-{anchor_id}"
                                title_text = options['title'] if options['title'] else ''
                                replacement_parts.append(f'''
                                    <h3 class="card-title mb-0">{title_text}</h3>
                                    <button class="btn btn-sm btn-outline-secondary" type="button"
                                            data-bs-toggle="collapse" data-bs-target="#{collapse_id}"
                                            aria-expanded="true" aria-controls="{collapse_id}">
                                        <i class="fas fa-chevron-up collapse-icon"></i>
                                    </button>
                                ''')
                            else:
                                # Just title, no collapse button
                                replacement_parts.append(f'<h3 class="card-title mb-0">{options["title"]}</h3>')

                            replacement_parts.append('</div>')  # End card-header

                        # Start card body (collapsible or not)
                        if options['collapsible']:
                            collapse_id = f"collapse-{anchor_id}"
                            replacement_parts.append(f'<div class="collapse show" id="{collapse_id}">')

                        replacement_parts.append('<div class="card-body d-flex flex-column">')

                        # Store collapse_id and back_to_top flag for the end tag
                        # We'll use a simple marker system
                        if options['collapsible'] or options['back_to_top']:
                            replacement_parts.append(f'[[BLOCK_OPTIONS:{anchor_id}:{options["collapsible"]}:{options["back_to_top"]}]]')

                        replacement = ''.join(replacement_parts)

                    elif action == 'end':
                        # Check if this block has options markers
                        # Search backwards from current position for options marker
                        before_text = rendered_text[:match.start()]
                        options_match = re.search(r'\[\[BLOCK_OPTIONS:([^:]+):([^:]+):([^\]]+)\]\](?!.*\[\[BLOCK_OPTIONS)', before_text)

                        replacement_parts = []

                        if options_match:
                            anchor_id = options_match.group(1)
                            is_collapsible = options_match.group(2) == 'True'
                            has_back_to_top = options_match.group(3) == 'True'

                            # Add back to top button if requested
                            if has_back_to_top:
                                replacement_parts.append('''
                                    <div class="text-end mt-3">
                                        <a href="#top" class="btn btn-sm btn-outline-primary">
                                            <i class="fas fa-arrow-up"></i> Back to Top
                                        </a>
                                    </div>
                                ''')

                            # Remove the options marker
                            rendered_text = rendered_text.replace(options_match.group(0), '', 1)

                        replacement_parts.append('</div>')  # End card-body

                        # Close collapse div if it exists
                        if options_match and options_match.group(2) == 'True':
                            replacement_parts.append('</div>')  # End collapse

                        replacement_parts.append('</div>')  # End card
                        replacement = ''.join(replacement_parts)

                elif container_type == 'cell':
                    # Cell: param is the width
                    if action == 'start':
                        if param:
                            # Parse width - support percentages, px, or Bootstrap col classes
                            width_style = self._parse_cell_width(param)
                            replacement = f'[[CELL_START:{width_style}]]'
                        else:
                            # No width specified - flex auto
                            replacement = '[[CELL_START:class="cell-block" style="flex: 1; min-width: 0;"]]'
                    elif action == 'end':
                        replacement = '[[CELL_END]]'

                rendered_text = rendered_text.replace(full_match, replacement, 1)
                match = re.search(self.container_regex, rendered_text)

                security_breaker += 1
                if security_breaker > 50:
                    raise PreRenderError("Too many container elements.")

            # Second pass: Wrap consecutive cells in row containers
            rendered_text = self._wrap_cells_in_rows(rendered_text)

        else:
            raise PreRenderError("Container tags are not well-formed.")
        return rendered_text

    def _clean_template_tag_wrappers(self, text):
        """Remove <p> tags that only wrap template tags like [[start_cell]], [[end_cell]], etc."""
        # Remove <p>[[tag]]</p> patterns
        text = re.sub(r'<p>\s*(\[\[(?:start|end)_(?:cell|block)[^\]]*\]\])\s*</p>', r'\1', text)
        # Remove empty <p></p> tags
        text = re.sub(r'<p>\s*</p>', '', text)
        # Remove <br> tags right after/before cell markers
        text = re.sub(r'(\[\[(?:CELL_(?:START|END)|start|end)_[^\]]*\]\])\s*<br\s*/?>', r'\1', text)
        text = re.sub(r'<br\s*/?>\s*(\[\[(?:CELL_(?:START|END)|start|end)_[^\]]*\]\])', r'\1', text)
        return text

    def _wrap_cells_in_rows(self, text):
        """Wrap consecutive cells in a flex row container."""
        # Find sequences of [[CELL_START:...]]...[[CELL_END]]
        # and wrap them in a row div

        # Pattern: one or more cell blocks
        cell_pattern = r'(\[\[CELL_START:[^\]]+\]\].*?\[\[CELL_END\]\])'

        # Find all positions where cells appear consecutively
        result = []
        pos = 0

        while pos < len(text):
            # Look for a cell start
            cell_start_match = re.search(r'\[\[CELL_START:', text[pos:])

            if not cell_start_match:
                # No more cells, append rest of text
                result.append(text[pos:])
                break

            # Append text before cell
            result.append(text[pos:pos + cell_start_match.start()])
            pos += cell_start_match.start()

            # Collect consecutive cells
            cells = []
            while True:
                cell_match = re.match(r'\[\[CELL_START:([^\]]+)\]\](.*?)\[\[CELL_END\]\]', text[pos:], re.DOTALL)
                if cell_match:
                    attr = cell_match.group(1)
                    content = cell_match.group(2)
                    # Create cell div - attr already contains the full attribute (class="..." or style="...")
                    cells.append(f'<div {attr}>{content}</div>')
                    pos += cell_match.end()

                    # Check if next thing is another cell
                    next_text = text[pos:].lstrip()
                    if not next_text.startswith('[[CELL_START:'):
                        break
                    pos = pos + (len(text[pos:]) - len(next_text))
                else:
                    break

            # Wrap collected cells in a row
            if cells:
                result.append('<div class="cell-row" style="display: flex; gap: 1rem; align-items: flex-start; flex-wrap: wrap;">')
                result.append(''.join(cells))
                result.append('</div>')

        return ''.join(result)

    def _parse_cell_width(self, width_param):
        """Parse cell width parameter and return appropriate style attribute.

        Supports:
        - Percentages: 40%, 33.33%
        - Pixels: 300px
        - Bootstrap col classes: col-4, col-md-6
        - Multiple Bootstrap classes: col-md-4,col-sm-12
        """
        width_param = width_param.strip()

        # Check if it's Bootstrap col classes (starts with 'col-')
        if width_param.startswith('col-'):
            classes = width_param.replace(',', ' ')
            return f'class="cell-block {classes}"'

        # Otherwise treat as width value (40%, 300px, etc.)
        # Use flex-basis for proper flex layout
        return f'class="cell-block" style="flex: 0 0 {width_param}; min-width: 0;"'

    def create_ui_elements(self):
        """Creates UI elements."""
        rendered_text = self.text
        match = re.search(self.ui_element_regex, rendered_text)
        security_breaker = 0
        while match:
            element_name = match.groups()[0]
            rendered_text = self.render_ui_element(element_name=element_name, text=rendered_text)
            match = re.search(self.ui_element_regex, rendered_text)

            security_breaker += 1
            if security_breaker > self.MAX_ITERATIONS:
                raise PreRenderError("Too many UI element rendering iterations.")
        return rendered_text

    def create_links(self):
        """Creates links."""
        rendered_text = self.text
        match = re.search(self.link_element_regex, rendered_text)
        security_breaker = 0
        while match:
            groups = match.groups()
            template = groups[0]  # file, page, orcid, plotly
            render_type = groups[1] if len(groups) > 1 else None  # btn, href, or None
            style = groups[2] if len(groups) > 2 else None  # primary, secondary, etc
            size = groups[3] if len(groups) > 3 else None  # sm, lg, or None
            element_id = groups[4] if len(groups) > 4 else groups[1]  # identifier/viewname
            custom_label = groups[5] if len(groups) > 5 else None  # optional label override

            rendered_text = self.render_element(template=template,
                                                element_id=element_id,
                                                render_type=render_type,
                                                style=style,
                                                size=size,
                                                custom_label=custom_label,
                                                text=rendered_text)

            match = re.search(self.link_element_regex, rendered_text)

            security_breaker += 1
            if security_breaker > self.MAX_ITERATIONS:
                raise PreRenderError("Too many link elements rendering iterations.")
        return rendered_text

    def create_urls(self):
        """Creates URL strings for pages."""
        rendered_text = self.text
        match = re.search(self.url_element_regex, rendered_text)
        security_breaker = 0
        while match:
            page_name = match.groups()[0]
            try:
                page = NdrCorePage.objects.get(view_name=page_name)
                url = page.url()
            except NdrCorePage.DoesNotExist:
                url = f"#page-not-found-{page_name}"

            rendered_text = rendered_text.replace(f'[[url|{page_name}]]', url)
            match = re.search(self.url_element_regex, rendered_text)

            security_breaker += 1
            if security_breaker > self.MAX_ITERATIONS:
                raise PreRenderError("Too many URL rendering iterations.")
        return rendered_text

    def create_settings(self):
        """Replaces [[setting|setting_name]] with custom setting values."""
        from ndr_core.models import NdrCoreValue

        rendered_text = self.text
        match = re.search(self.setting_regex, rendered_text)
        security_breaker = 0
        while match:
            setting_name = match.groups()[0]
            try:
                setting = NdrCoreValue.objects.get(value_name=setting_name)
                value = setting.get_value()
            except NdrCoreValue.DoesNotExist:
                value = f"[Setting '{setting_name}' not found]"

            rendered_text = rendered_text.replace(f'[[setting|{setting_name}]]', str(value))
            match = re.search(self.setting_regex, rendered_text)

            security_breaker += 1
            if security_breaker > self.MAX_ITERATIONS:
                raise PreRenderError("Too many setting rendering iterations.")
        return rendered_text

    def create_toc(self):
        """Creates table of contents with anchor links to titled blocks."""
        rendered_text = self.text
        match = re.search(self.toc_regex, rendered_text)

        if match and self.block_titles:
            toc_html = '<div class="card mb-3 toc-container">'
            toc_html += '<div class="card-body">'
            toc_html += '<h4 class="card-title">Table of Contents</h4>'
            toc_html += '<ul class="list-unstyled">'

            for block in self.block_titles:
                toc_html += f'<li><a href="#{block["anchor"]}">{block["title"]}</a></li>'

            toc_html += '</ul>'
            toc_html += '</div>'
            toc_html += '</div>'

            rendered_text = rendered_text.replace('[[toc]]', toc_html)
        elif match and not self.block_titles:
            # If [[toc]] is present but no titled blocks exist, remove the tag
            rendered_text = rendered_text.replace('[[toc]]', '')

        return rendered_text

    def create_floats(self):
        """Replaces float tags with a flexbox side-by-side layout.

        Usage:
            [[float_right]]
            [[element|my_card]]
            [[float_text]]
            Text that appears to the LEFT of the card.
            [[end_float]]

        [[float_right]] puts the element on the right, text on the left.
        [[float_left]]  puts the element on the left, text on the right.
        [[float_text]]  separates the element from the wrapping text.
        [[end_float]]   closes the layout.
        """
        rendered_text = self.text

        # Strip <p> tags that wrap individual float control tags
        rendered_text = re.sub(
            r'<p>\s*(\[\[(?:float_right|float_left|float_text|end_float)\]\])\s*</p>', r'\1', rendered_text
        )
        # Strip opening <p> that immediately precedes a float start (CKEditor wraps the whole construct)
        rendered_text = re.sub(
            r'<p>(\s*\[\[float_(?:right|left)\]\])', r'\1', rendered_text
        )
        # Strip closing </p> that immediately follows [[end_float]]
        rendered_text = re.sub(
            r'(\[\[end_float\]\]\s*)</p>', r'\1', rendered_text
        )
        # Strip stray <br> around float control tags
        rendered_text = re.sub(
            r'(\[\[(?:float_right|float_left|float_text|end_float)\]\])\s*<br\s*/?>', r'\1', rendered_text
        )
        rendered_text = re.sub(
            r'<br\s*/?>\s*(\[\[(?:float_right|float_left|float_text|end_float)\]\])', r'\1', rendered_text
        )
        # Strip &nbsp; entities, non-breaking spaces, and whitespace between
        # [[float_right/left]] and the following [[ tag (CKEditor inserts many &nbsp; between lines)
        rendered_text = re.sub(
            r'(\[\[float_(?:right|left)\]\])(?:[ \t\r\n\u00a0]|&nbsp;|<br\s*/?>)+(?=\[\[)',
            r'\1', rendered_text, flags=re.IGNORECASE
        )

        # float_right: row-reverse puts the first child (element) on the right
        rendered_text = rendered_text.replace(
            '[[float_right]]',
            '<div style="display:flex; flex-direction:row-reverse; gap:1.5rem; align-items:flex-start;">'
            '<div style="flex-shrink:0; width:fit-content;">'
        )
        # float_left: normal row puts the first child (element) on the left
        rendered_text = rendered_text.replace(
            '[[float_left]]',
            '<div style="display:flex; flex-direction:row; gap:1.5rem; align-items:flex-start;">'
            '<div style="flex-shrink:0; width:fit-content;">'
        )
        # float_text: closes the element div, opens the text div
        rendered_text = rendered_text.replace(
            '[[float_text]]',
            '</div><div style="flex:1; min-width:0;">'
        )
        # end_float: closes the text div and the outer wrapper
        rendered_text = rendered_text.replace(
            '[[end_float]]',
            '</div></div>'
        )
        return rendered_text

    def create_code_blocks(self):
        """Creates code blocks with optional syntax highlighting and pretty-printing."""
        rendered_text = self.text
        security_breaker = 0

        # Find start tag
        start_match = re.search(self.code_start_regex, rendered_text)

        while start_match:
            language = start_match.group(1) if start_match.group(1) else 'text'
            start_pos = start_match.end()

            # Find corresponding end tag
            end_match = re.search(self.code_end_regex, rendered_text[start_pos:])
            if not end_match:
                # No matching end tag found
                break

            end_pos = start_pos + end_match.start()

            # Extract content between tags
            code_content = rendered_text[start_pos:end_pos]

            # Strip HTML tags (like <p>, <br>, etc.) inserted by WYSIWYG editor
            # First, convert line break tags to newlines to preserve formatting
            code_content = re.sub(r'<br\s*/?>', '\n', code_content, flags=re.IGNORECASE)
            code_content = re.sub(r'</p>\s*<p>', '\n', code_content, flags=re.IGNORECASE)
            # Remove remaining HTML tags but preserve the text content
            code_content = re.sub(r'<[^>]+>', '', code_content)

            # Unescape HTML entities that might be in the content
            code_content = html.unescape(code_content)

            # Strip leading/trailing whitespace but preserve internal formatting
            code_content = code_content.strip()

            # Pretty-print JSON if language is json
            if language.lower() == 'json':
                try:
                    # Replace non-breaking spaces with regular spaces (CKEditor inserts these)
                    code_content_cleaned = code_content.replace('\xa0', ' ').replace('\u00a0', ' ')

                    parsed_json = json.loads(code_content_cleaned)
                    code_content = json.dumps(parsed_json, indent=2, ensure_ascii=False)
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON content; skipping pretty-printing. Error: {e}")
                    pass

            # Escape HTML to prevent XSS
            code_content = html.escape(code_content)

            # Create the code block with language class for syntax highlighting
            code_html = f'<pre class="code-block"><code class="language-{language.lower()}">{code_content}</code></pre>'

            # Replace the entire block (from start tag to end tag) with the rendered HTML
            full_block = rendered_text[start_match.start():start_pos + end_match.end()]
            rendered_text = rendered_text.replace(full_block, code_html, 1)

            # Search for next code block
            start_match = re.search(self.code_start_regex, rendered_text)

            security_breaker += 1
            if security_breaker > self.MAX_ITERATIONS:
                raise PreRenderError("Too many code block rendering iterations.")

        return rendered_text


    def render_ui_element(self, element_name, text):
        """Renders a UI element by name."""
        try:
            element = NdrCoreUIElement.objects.get(name=element_name)
        except NdrCoreUIElement.DoesNotExist:
            error_html = f"<span class='text-danger'>UI Element not found: {element_name}</span>"
            return text.replace(f"[[element|{element_name}]]", error_html)

        # Get the template name from the element type
        template_name = element.type

        # Build context for rendering
        context = {'data': element, 'request': self.request}

        # Special handling for DATA_OBJECT type
        if element.type == NdrCoreUIElement.UIElementType.DATA_OBJECT:
            try:
                # Render single data object (Data Object is now single-item type)
                rendered_item = None
                items = element.items()
                if items:
                    item = items[0]  # Get first (and only) item
                    if item.search_configuration and item.object_id and item.result_field:
                        # Fetch data from API
                        api_result = self._fetch_data_object(item.search_configuration, item.object_id)

                        if api_result:
                            # Render using result field's rich_expression
                            template_string = TemplateString(
                                item.result_field.rich_expression, api_result, show_errors=True
                            )
                            field_content = template_string.get_formatted_string()
                            field_content = template_string.sanitize_html(field_content)

                            rendered_item = field_content

                context['rendered_item'] = rendered_item
            except Exception as e:
                error_html = f"<span class='text-danger'>Error fetching data: {e}</span>"
                return text.replace(f'[[element|{element_name}]]', error_html)

        # Special handling for manifest viewer
        if element.type == NdrCoreUIElement.UIElementType.MANIFEST_VIEWER:
            group_id = element.items().first().manifest_group if element and element.items().exists() else None
            context['manifest_selection_form'] = ManifestSelectionForm(self.request.GET or None, manifest_group=group_id)

        # Special handling for VIDEO type
        if element.type == NdrCoreUIElement.UIElementType.VIDEO:
            items = element.items()
            if items:
                item = items[0]
                context['provider'] = item.provider
                context['video_id'] = item.object_id
                context['video_title'] = item.title
                context['video_description'] = item.text

        # Special handling for AUDIO type
        if element.type == NdrCoreUIElement.UIElementType.AUDIO:
            items = element.items()
            if items:
                item = items[0]
                context['audio_file'] = item.upload_file
                context['audio_title'] = item.title
                context['audio_description'] = item.text

        # Special handling for PDF_VIEWER type
        if element.type == NdrCoreUIElement.UIElementType.PDF_VIEWER:
            items = element.items()
            if items:
                context['pdf_files'] = [item.upload_file for item in items if item.upload_file]
                context['pdf_title'] = items[0].title
                context['pdf_description'] = items[0].text
                try:
                    context['pdf_height'] = int(items[0].object_id) if items[0].object_id else 800
                except (ValueError, TypeError):
                    context['pdf_height'] = 800

        # Special handling for ACADEMIC_ABOUT type
        if element.type == NdrCoreUIElement.UIElementType.ACADEMIC_ABOUT:
            items = element.items()
            if items:
                item = items[0]
                context['profile_image'] = item.ndr_image
                context['person_name'] = item.title
                context['title_position'] = item.text
                context['bio'] = item.rich_text
                context['website'] = item.url
                context['orcid_id'] = item.object_id

        # Special handling for TEAM_GRID type
        if element.type == NdrCoreUIElement.UIElementType.TEAM_GRID:
            context['team_members'] = element.items()  # Already ordered by order_idx
            context['columns_layout'] = getattr(element, '_columns_layout', 'auto')
            context['show_bios'] = getattr(element, '_show_bios', True)
            context['card_style'] = getattr(element, '_card_style', 'standard')

        # Special handling for CARD_GRID type
        if element.type == NdrCoreUIElement.UIElementType.CARD_GRID:
            items = element.items()
            card_items = []
            for item in items:
                if item.object_id:
                    try:
                        card_items.append(NdrCoreUIElement.objects.get(name=item.object_id))
                    except NdrCoreUIElement.DoesNotExist:
                        pass
            context['card_items'] = card_items

        # Special handling for ZOTERO_GROUP type
        if element.type == NdrCoreUIElement.UIElementType.ZOTERO_GROUP:
            items = element.items()
            if items:
                item = items[0]
                group_id = item.object_id
                api_key = item.text
                section_title = item.title
                items_per_page, cache_ttl_hours = self._parse_zotero_provider(item.provider)

                zotero_all_items = []
                zotero_error = None

                if group_id:
                    import hashlib as _hashlib
                    key_hash = _hashlib.md5(api_key.encode()).hexdigest()[:8] if api_key else 'pub'
                    cache_key = f'ndr_zotero_{re.sub(r"[^a-zA-Z0-9]", "_", group_id)}_{key_hash}'

                    from django.core.cache import cache as _cache
                    zotero_all_items = _cache.get(cache_key)

                    if zotero_all_items is None:
                        try:
                            zotero_all_items = self._fetch_all_zotero_items(group_id, api_key)
                            _cache.set(cache_key, zotero_all_items, timeout=cache_ttl_hours * 3600)
                        except Exception as exc:
                            zotero_error = str(exc)
                            zotero_all_items = []
                else:
                    zotero_error = 'No Zotero group ID configured.'

                # Pagination
                page_param = f'zotero_p_{element.name}'
                try:
                    current_page = max(1, int(self.request.GET.get(page_param, 1)))
                except (ValueError, TypeError):
                    current_page = 1

                total_items = len(zotero_all_items)
                total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
                current_page = min(current_page, total_pages)

                start_idx = (current_page - 1) * items_per_page
                end_idx = start_idx + items_per_page

                # Build base URL for pagination links (preserves existing query params)
                query = self.request.GET.copy()
                query.pop(page_param, None)
                base_query = query.urlencode()
                page_base_url = (
                    f'{self.request.path}?{base_query}&{page_param}='
                    if base_query else
                    f'{self.request.path}?{page_param}='
                )

                context.update({
                    'zotero_items': zotero_all_items[start_idx:end_idx],
                    'zotero_section_title': section_title,
                    'zotero_error': zotero_error,
                    'zotero_page': current_page,
                    'zotero_total_pages': total_pages,
                    'zotero_total_items': total_items,
                    'zotero_page_start': start_idx + 1,
                    'zotero_page_end': min(end_idx, total_items),
                    'zotero_page_base_url': page_base_url,
                    'zotero_page_range': self._build_page_range(current_page, total_pages),
                    'zotero_prev_page': max(1, current_page - 1),
                    'zotero_next_page': min(total_pages, current_page + 1),
                })
            else:
                context['zotero_error'] = 'No configuration found.'

        # Special handling for JS_MODULE type
        if element.type == NdrCoreUIElement.UIElementType.JS_MODULE:
            items = element.items()
            if items:
                item = items[0]
                context['module_config'] = item.js_module_config
                context['module_package'] = item.js_module_package

        # Render the template
        try:
            element_html_string = render_to_string(f'ndr_core/ui_elements/{template_name}.html',
                                                   request=self.request, context=context)
            text = text.replace(f'[[element|{element_name}]]', element_html_string)
        except Exception as e:
            error_html = f"<span class='text-danger'>Error rendering element {element_name}: {e}</span>"
            text = text.replace(f'[[element|{element_name}]]', error_html)

        return text

    def _fetch_data_object(self, search_configuration, object_id):
        """Fetches a single data object from the API."""

        # Create API query
        factory = ApiFactory(search_configuration)
        query_obj = factory.get_query_instance()

        # Execute query
        query = query_obj.get_record_query(object_id)
        result_obj = factory.get_result_instance(query, self.request)
        result_obj.load_result()

        # Return the first result if available
        if result_obj and result_obj.results and len(result_obj.results) > 0:
            # print(f"Fetched data object with ID: {result_obj.results}")
            return result_obj.results[0]['data']

        return None

    def _parse_zotero_provider(self, provider_value):
        """Parse provider field: 'items_per_page' or 'items_per_page:cache_ttl_hours'."""
        if ':' in (provider_value or ''):
            parts = provider_value.split(':', 1)
            try:
                items_per_page = max(1, int(parts[0]))
            except (ValueError, TypeError):
                items_per_page = 20
            try:
                cache_ttl_hours = max(1, int(parts[1]))
            except (ValueError, TypeError):
                cache_ttl_hours = 24
        else:
            try:
                items_per_page = max(1, int(provider_value)) if provider_value else 20
            except (ValueError, TypeError):
                items_per_page = 20
            cache_ttl_hours = 24
        return items_per_page, cache_ttl_hours

    def _fetch_all_zotero_items(self, group_id, api_key=None, max_total=1000):
        """Fetch all top-level items from a Zotero group library, handling API pagination."""
        import requests as _requests

        all_items = []
        start = 0
        batch = 100  # Zotero API maximum per request

        headers = {'Zotero-API-Version': '3'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        while len(all_items) < max_total:
            response = _requests.get(
                f'https://api.zotero.org/groups/{group_id}/items/top',
                params={
                    'limit': min(batch, max_total - len(all_items)),
                    'start': start,
                    'format': 'json',
                    'sort': 'date',
                    'direction': 'desc',
                },
                headers=headers,
                timeout=10,
            )
            if response.status_code == 403:
                raise Exception('Access denied. Check the API key or make the library public.')
            if response.status_code == 404:
                raise Exception('Group library not found. Check the group ID.')
            response.raise_for_status()

            batch_items = response.json()
            if not batch_items:
                break

            all_items.extend(batch_items)
            start += len(batch_items)

            total = int(response.headers.get('Total-Results', 0))
            if start >= total:
                break

        return all_items

    def _build_page_range(self, current, total, window=2):
        """Return list of page numbers with None as ellipsis markers."""
        if total <= 1:
            return []
        pages = set()
        pages.add(1)
        pages.add(total)
        for i in range(max(1, current - window), min(total, current + window) + 1):
            pages.add(i)
        result = []
        prev = None
        for p in sorted(pages):
            if prev is not None and p - prev > 1:
                result.append(None)
            result.append(p)
            prev = p
        return result

    def render_element(self, template, element_id, text, render_type=None, style=None, size=None, custom_label=None):
        """Renders an element with optional styling parameters."""
        if template == "orcid":
            # Validate ORCID format
            orcid_pattern = r"^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$"
            if not re.match(orcid_pattern, element_id):
                return text.replace(f"[[{template}|{element_id}]]",
                                    f"<span class='text-danger'>Invalid ORCID: {element_id}</span>")

            # Generate ORCID link
            orcid_url = f"https://orcid.org/{element_id}"
            orcid_icon_url = static('ndr_core/images/orcid.svg')
            orcid_html = f"""
            <a href="{orcid_url}" target="_blank" class="orcid-link" rel="noopener noreferrer">
                <img src="{orcid_icon_url}" alt="ORCID" style="width: 16px; height: 16px; vertical-align: middle;">
                {element_id}
            </a>
            """
            return text.replace(f"[[{template}|{element_id}]]", orcid_html)

        if template == "link":
            # Direct external URL — no database lookup needed
            url = element_id
            label = custom_label or url

            if render_type == "btn":
                css_class = f"btn btn-{style or 'primary'}"
                if size:
                    css_class += f" btn-{size}"
                link_html = f'<a href="{url}" class="{css_class}" target="_blank" rel="noopener noreferrer">{label}</a>'
            elif style:
                link_html = f'<a href="{url}" class="link-{style}" target="_blank" rel="noopener noreferrer">{label}</a>'
            else:
                link_html = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>'

            # Reconstruct the original tag to replace
            if render_type or style or size:
                tag_parts = ["link"]
                if render_type:
                    tag_parts.append(render_type)
                if style:
                    tag_parts.append(style)
                if size:
                    tag_parts.append(size)
                original_tag = f'[[{"-".join(tag_parts)}|{url}]]'
            else:
                original_tag = f'[[link|{url}]]'
            if custom_label is not None:
                original_tag = original_tag[:-2] + f'|{custom_label}]]'

            return text.replace(original_tag, link_html)

        if template == "image":
            element = self.get_element(template, element_id)
            if element is None:
                error_html = f"<span class='text-danger'>Image not found: {element_id}</span>"
                return text.replace(f'[[image|{element_id}]]', error_html)

            alt = custom_label or element.alt_text or ''
            img_attrs = f'src="{element.image.url}" alt="{alt}" class="img-fluid"'
            # -width-NNN → max-width constraint
            if render_type == 'width' and style:
                img_attrs += f' style="max-width:{style}px;"'

            img_html = f'<img {img_attrs}>'

            # Reconstruct original tag for replacement
            if render_type and style:
                orig = f'[[image-{render_type}-{style}|{element_id}]]'
            else:
                orig = f'[[image|{element_id}]]'
            if custom_label is not None:
                orig = orig[:-2] + f'|{custom_label}]]'

            return text.replace(orig, img_html)

        if template == "plotly":
            # Reconstruct the original tag (may include options like -height-800)
            options_str = ''
            if render_type:
                options_str += f'-{render_type}'
                if style:
                    options_str += f'-{style}'
                    if size:
                        options_str += f'-{size}'
            original_tag = f'[[{template}{options_str}|{element_id}]]'

            # Build config dict from parsed options (e.g. -height-800 → {'height': '800'})
            config = {}
            if render_type and style:
                config[render_type] = style

            # Load the JSON file and render as Plotly chart
            element = self.get_element(template, element_id)
            if element is None:
                error_html = f"<span class='text-danger'>Plotly file not found: {element_id}</span>"
                return text.replace(original_tag, error_html)

            try:
                # Read file content
                file_path = element.file.path
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()

                # Parse JSON
                plotly_data = json.loads(file_content)

                # Import PlotlyFilter
                from ndr_core.ndr_templatetags.filters import PlotlyFilter

                # Render using PlotlyFilter
                plotly_filter = PlotlyFilter('plotly', plotly_data, config, None)
                plotly_html = plotly_filter.get_rendered_value()

                return text.replace(original_tag, plotly_html)

            except FileNotFoundError:
                error_html = f"<span class='text-danger'>Plotly file not found on disk: {element_id}</span>"
                return text.replace(original_tag, error_html)
            except json.JSONDecodeError as e:
                error_html = f"<span class='text-danger'>Invalid JSON in Plotly file: {e}</span>"
                return text.replace(original_tag, error_html)
            except Exception as e:
                error_html = f"<span class='text-danger'>Error rendering Plotly chart: {e}</span>"
                return text.replace(original_tag, error_html)

        # Split query string from element_id before lookup (only relevant for page links)
        lookup_id = element_id
        query_string = None
        if template == 'page' and '?' in element_id:
            lookup_id, query_string = element_id.split('?', 1)
            # Unescape HTML entities in the query string only (e.g. &amp; → &)
            # element_id itself is kept encoded for the text.replace() call later
            import html as _html
            query_string = _html.unescape(query_string)

        element = self.get_element(template, lookup_id)

        # Build the final href for page links (base URL + optional query string)
        page_href = None
        if template == 'page' and element is not None:
            page_href = element.url()
            if query_string:
                page_href = f"{page_href}?{query_string}"

        # Build context with element data and styling parameters
        context = {
            'data': element,
            'render_type': render_type or ('href' if template == 'page' else None),
            'style': style or ('secondary' if template == 'page' else None),
            'size': size,
            'custom_label': custom_label,
            'page_href': page_href,
        }

        if isinstance(element, NdrCoreUIElement) and element.type == NdrCoreUIElement.UIElementType.MANIFEST_VIEWER:
            group_id = element.items().first().manifest_group if element and element.items().exists() else None
            context['manifest_selection_form'] = ManifestSelectionForm(self.request.GET or None, manifest_group=group_id)

        element_html_string = render_to_string(f'ndr_core/ui_elements/{template}.html',
                                               request=self.request, context=context)

        # Build the original tag pattern to replace
        if render_type or style or size:
            tag_parts = [template]
            if render_type:
                tag_parts.append(render_type)
            if style:
                tag_parts.append(style)
            if size:
                tag_parts.append(size)
            original_tag = f'[[{"-".join(tag_parts)}|{element_id}]]'
        else:
            original_tag = f'[[{template}|{element_id}]]'
        if custom_label is not None:
            original_tag = original_tag[:-2] + f'|{custom_label}]]'

        text = text.replace(original_tag, element_html_string)

        return text

    def get_element(self, template, element_id):
        """Returns an element."""
        if template == 'page':
            return self._get_page_element(element_id)

        if template in self.link_element_classes:
            element_class = self.link_element_classes[template]
        else:
            element_class = NdrCoreUIElement

        try:
            if template in self.link_element_keys:
                kw = {self.link_element_keys[template]: element_id}
            else:
                if element_id.isnumeric():
                    kw = {'pk': int(element_id)}
                else:
                    kw = {'pk': element_id}
            element = element_class.objects.get(**kw)
            return element
        except element_class.DoesNotExist:
            return None

    def _get_page_element(self, element_id):
        """Looks up a page by view_name (top-level) or parent/child path.

        For a plain view_name (no slash): tries top-level first, then falls back
        to any page with that view_name if exactly one match exists.
        """
        try:
            if '/' in element_id:
                parent = None
                page = None
                for segment in element_id.split('/'):
                    page = NdrCorePage.objects.get(view_name=segment, parent_page=parent)
                    parent = page
                return page
            else:
                try:
                    return NdrCorePage.objects.get(view_name=element_id, parent_page=None)
                except NdrCorePage.DoesNotExist:
                    pages = NdrCorePage.objects.filter(view_name=element_id)
                    if pages.count() == 1:
                        return pages.first()
                    return None
        except NdrCorePage.DoesNotExist:
            return None

    def get_pre_rendered_text(self):
        """Returns the pre-rendered text."""
        if self.text is None:
            raise PreRenderError("Text must not be None")
        if self.text == '':
            return self.text

        try:
            self.text = self.create_code_blocks()
            self.text = self.create_containers()
            self.text = self.create_floats()
            self.text = self.create_toc()
            self.text = self.create_ui_elements()
            self.text = self.create_settings()
            self.text = self.create_links()
        except PreRenderError as e:
            raise e
        return self.text
