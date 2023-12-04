class ColorOptionMixin:
    """ A mixin for color options.
    Example: {test_value|pill:color=primary}"""

    color_options = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark']
    color = None

    @staticmethod
    def get_color_from_value(value, lightness=50):
        """Translates a value to a color."""
        if value is None:
            return ''

        hash_value = 0
        for char in value:
            hash_value = ord(char) + ((hash_value << 5) - hash_value)
            hash_value = hash_value & hash_value

        return f'hsl({hash_value % 360}, {100}%, {lightness}%)'

    def get_color_string(self, color_option, data=None):
        """Returns the color."""
        if color_option:

            if color_option in self.color_options:
                return f'color: {color_option};'
            if color_option.startswith('#') or color_option.startswith('rgb') or color_option.startswith('hsl'):
                return f'color: {color_option};'
            if color_option.startswith('val__'):
                if data:
                    try:
                        return f'color: {data[color_option[5:]]};'
                    except KeyError:
                        return ''
                else:
                    return ''
            if color_option.startswith('byval__'):
                if data:
                    try:
                        value = data[color_option[7:]]
                        return f'color: {self.get_color_from_value(value)};'
                    except KeyError:
                        return ''
                else:
                    return ''

            color = f'color: {color_option};'
        else:
            color = ''

        return color

    def set_color(self, color):
        """Sets the color."""
        if color in self.color_options:
            self.color = color
        else:
            raise ValueError(f"Color {color} not found.")
