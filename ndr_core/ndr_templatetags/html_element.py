
class HTMLElement:
    """A class to represent an HTML element."""

    COLOR_CLASSES = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark']
    HTML_COLOR_NAMES = [
        "AliceBlue", "AntiqueWhite", "Aqua", "Aquamarine", "Azure",
        "Beige", "Bisque", "Black", "BlanchedAlmond", "Blue",
        "BlueViolet", "Brown", "BurlyWood", "CadetBlue", "Chartreuse",
        "Chocolate", "Coral", "CornflowerBlue", "Cornsilk", "Crimson",
        "Cyan", "DarkBlue", "DarkCyan", "DarkGoldenRod", "DarkGray",
        "DarkGrey", "DarkGreen", "DarkKhaki", "DarkMagenta", "DarkOliveGreen",
        "DarkOrange", "DarkOrchid", "DarkRed", "DarkSalmon", "DarkSeaGreen",
        "DarkSlateBlue", "DarkSlateGray", "DarkSlateGrey", "DarkTurquoise", "DarkViolet",
        "DeepPink", "DeepSkyBlue", "DimGray", "DimGrey", "DodgerBlue",
        "FireBrick", "FloralWhite", "ForestGreen", "Fuchsia", "Gainsboro",
        "GhostWhite", "Gold", "GoldenRod", "Gray", "Grey",
        "Green", "GreenYellow", "HoneyDew", "HotPink", "IndianRed",
        "Indigo", "Ivory", "Khaki", "Lavender", "LavenderBlush",
        "LawnGreen", "LemonChiffon", "LightBlue", "LightCoral", "LightCyan",
        "LightGoldenRodYellow", "LightGray", "LightGrey", "LightGreen", "LightPink",
        "LightSalmon", "LightSeaGreen", "LightSkyBlue", "LightSlateGray", "LightSlateGrey",
        "LightSteelBlue", "LightYellow", "Lime", "LimeGreen", "Linen",
        "Magenta", "Maroon", "MediumAquaMarine", "MediumBlue", "MediumOrchid",
        "MediumPurple", "MediumSeaGreen", "MediumSlateBlue", "MediumSpringGreen", "MediumTurquoise",
        "MediumVioletRed", "MidnightBlue", "MintCream", "MistyRose", "Moccasin",
        "NavajoWhite", "Navy", "OldLace", "Olive", "OliveDrab",
        "Orange", "OrangeRed", "Orchid", "PaleGoldenRod", "PaleGreen",
        "PaleTurquoise", "PaleVioletRed", "PapayaWhip", "PeachPuff", "Peru",
        "Pink", "Plum", "PowderBlue", "Purple", "Red",
        "RosyBrown", "RoyalBlue", "SaddleBrown", "Salmon", "SandyBrown",
        "SeaGreen", "SeaShell", "Sienna", "Silver", "SkyBlue",
        "SlateBlue", "SlateGray", "SlateGrey", "Snow", "SpringGreen",
        "SteelBlue", "Tan", "Teal", "Thistle", "Tomato",
        "Turquoise", "Violet", "Wheat", "White", "WhiteSmoke",
        "Yellow", "YellowGreen"
    ]

    def __init__(self, tag, attrs=None, content=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.content = content or []

    def __str__(self):
        return self.render()

    def render(self):
        """Renders the element."""
        attrs = self.render_attrs()
        content = self.render_content()
        return f"<{self.tag}{attrs}>{content}</{self.tag}>"

    def render_attrs(self):
        """Renders the attributes of the element."""
        # Remove duplicate attributes
        for key, value in self.attrs.items():
            self.attrs[key] = list(set(value))

        # Sort attribute items
        for key, value in self.attrs.items():
            self.attrs[key] = sorted(value)

        # Sort attributes
        self.attrs = dict(sorted(self.attrs.items()))

        # Render attributes
        attrs = ""
        for key, value in self.attrs.items():
            attrs += f' {key}="{" ".join(value)}"'
        return attrs

    def render_content(self):
        """Renders the content of the element."""
        content = ""
        for item in self.content:
            content += str(item)
        return content

    def add_attribute(self, key, value):
        """Adds an attribute."""
        if key not in self.attrs:
            self.attrs[key] = []
        self.attrs[key].append(value)

    def add_content(self, content):
        """Adds content."""
        self.content.append(content)

    def manage_color_attribute(self, option_name, option_value, value, data):
        """Manages the color attribute. option_name can be 'color' or 'bg'.
        The value can be a bootstrap class name, a color name, a hex value, a rgb value, a hsl value,
        a value from the data dictionary."""

        # print(option_name, option_value, value, data)

        if option_value in self.COLOR_CLASSES:
            self.add_attribute('class', f"badge-{value}")

        color_style_string = 'color'
        if option_name == 'bg':
            color_style_string = 'background-color'

        if option_value in self.HTML_COLOR_NAMES:
            self.add_attribute('style', f'{color_style_string}: {option_value};')
        if option_value.startswith('#') or option_value.startswith('rgb') or option_value.startswith('hsl'):
            self.add_attribute('style', f'{color_style_string}: {option_value};')
        if option_value.startswith('val__'):
            self.add_attribute('style', f'{color_style_string}: niy;')
        if option_value.startswith('byval__'):
            self.add_attribute('style', f'{color_style_string}: niy;')
        if option_value == 'byval':
            self.add_attribute('style', f'{color_style_string}: {self.get_color_from_value(value)};')

    @staticmethod
    def get_color_from_value(value, lightness=80):
        """Translates a value to a color."""
        if value is None:
            return ''

        value = str(value)
        hash_value = 0
        for char in value:
            hash_value = ord(char) + ((hash_value << 5) - hash_value)
            hash_value = hash_value & hash_value

        return f'hsl({hash_value % 360}, {100}%, {lightness}%)'
