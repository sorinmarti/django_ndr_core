from django.test import TestCase

from ndr_core.ndr_templatetags.html_element import HTMLElement


class TemplateStringTestCase(TestCase):

    def test_html_element(self):
        """ Tests the HTMLElement class."""
        element = HTMLElement("div", attrs={"class": ["test"]}, content=["Hello World"])
        self.assertEqual(str(element), '<div class="test">Hello World</div>')

    def test_html_element_creation(self):
        """ Tests the HTMLElement class."""
        element_1 = HTMLElement("div", attrs={"class": ["test"]}, content=["Hello World"])
        element_2 = HTMLElement("div")
        element_2.add_attribute("class", "test")
        element_2.add_content("Hello World")

        self.assertEqual(str(element_1), str(element_2))

    def test_multiple_attributes(self):
        """ Tests the HTMLElement class."""
        element = HTMLElement("div", attrs={"class": ["test"], "style": ["color: red"]}, content=["Hello World"])
        self.assertEqual(str(element), '<div class="test" style="color: red">Hello World</div>')

        element_2 = HTMLElement("div", attrs={"class": ["test", "test2"]})
        element_3 = HTMLElement("div", attrs={"class": ["test2", "test", "test"]})

        self.assertEqual(str(element_2), str(element_3))