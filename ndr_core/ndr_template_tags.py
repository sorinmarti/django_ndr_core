import re

from django.template.loader import render_to_string

from ndr_core.models import NdrCoreUIElement, NdrCoreImage, NdrCoreUpload, NdrCorePage


class TextPreRenderer:

    MAX_ITERATIONS = 50
    ui_element_regex = r'\[\[(card|slideshow|carousel|jumbotron|figure|banner)\|([0-9]*)\]\]'
    link_element_regex = r'\[\[(file|page)\|([0-9]*)\]\]'
    container_regex = r'\[\[(start|end)_(block)\]\]'
    link_element_classes = {'figure': NdrCoreImage, 'file': NdrCoreUpload, 'page': NdrCorePage}
    text = None

    def __init__(self, text, request):
        self.text = text
        self.request = request

    def check_tags_integrity(self):
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

        for item in items:
            if items[item]["start"] != items[item]["end"]:
                return False
        return True

    def create_containers(self):
        if self.check_tags_integrity():
            rendered_text = self.text
            match = re.search(self.container_regex, rendered_text)
            security_breaker = 0
            while match:
                rendered_text = rendered_text.replace(f'[[start_block]]',
                                                      '<div class="card mb-2 box-shadow">'
                                                      '<div class="card-body d-flex flex-column">')
                rendered_text = rendered_text.replace(f'[[end_block]]', '</div></div>')
                match = re.search(self.container_regex, rendered_text)

                security_breaker += 1
                if security_breaker > 50:
                    raise PreRenderError("Too many container elements.")
        else:
            raise PreRenderError("Container tags are not well-formed.")
        return rendered_text

    def create_ui_elements(self):
        rendered_text = self.text
        match = re.search(self.ui_element_regex, rendered_text)
        security_breaker = 0
        while match:
            rendered_text = self.render_element(template=match.groups()[0],
                                                element_id=match.groups()[1],
                                                text=rendered_text)
            match = re.search(self.ui_element_regex, rendered_text)

            security_breaker += 1
            if security_breaker > self.MAX_ITERATIONS:
                raise PreRenderError("Too many UI element rendering iterations.")
        return rendered_text

    def create_links(self):
        rendered_text = self.text
        match = re.search(self.link_element_regex, rendered_text)
        security_breaker = 0
        while match:
            rendered_text = self.render_element(template=match.groups()[0],
                                                element_id=match.groups()[1],
                                                text=rendered_text)

            match = re.search(self.link_element_regex, rendered_text)

            security_breaker += 1
            if security_breaker > self.MAX_ITERATIONS:
                raise PreRenderError("Too many link elements rendering iterations.")
        return rendered_text

    def render_element(self, template, element_id,  text):
        element = self.get_element(template, element_id)
        element_html_string = render_to_string(f'ndr_core/ui_elements/{template}.html',
                                               request=self.request, context={'data': element})
        text = text.replace(f'[[{template}|{element_id}]]', element_html_string)
        return text

    def get_element(self, template, element_id):
        if template in self.link_element_classes:
            element_class = self.link_element_classes[template]
        else:
            element_class = NdrCoreUIElement

        try:
            element = element_class.objects.get(id=int(element_id))
            return element
        except element_class.DoesNotExist:
            return None

    def get_pre_rendered_text(self):
        if self.text is None:
            raise PreRenderError("Text must not be None")
        if self.text == '':
            return self.text

        try:
            self.text = self.create_containers()
            self.text = self.create_ui_elements()
            self.text = self.create_links()
        except PreRenderError:
            print("Error")
        return self.text


class PreRenderError(Exception):
    """ TODO """
