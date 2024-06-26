"""This module contains functions to create a preview image of a form."""
import io
import math
from PIL import Image, ImageDraw
from ndr_core.models import NdrCoreSearchField


class PreviewImage:
    """This class provides functions to create a preview image of a form."""

    col_width = 60  # Width of a column in pixels. Maximum of columns is 12.
    row_height = 50  # Height of a row in pixels. Maximum of rows is 20.
    margin = 5  # Margin of a field in pixels.

    shadow_color = "#444444"  # Color of the shadow
    indicator_color = "#666666"  # Color of the field type indicator
    image_background_color = '#D3D3D3'  # Color of the background of the image
    field_color = "#FFFFFF"  # Color of the field
    text_color = "#000000"  # Color of the text

    def get_coordinates(self, row, start_col, width_cols, offset=0):
        """ A form is organized in rows and columns. This function returns the coordinates of a
        rectangle that represents a field in the form. The coordinates are returned as a list of
        tuples. The first tuple contains the coordinates of the top left corner of the rectangle.
        The second tuple contains the bottom right corner of the rectangle. The coordinates are
        in pixels."""

        x1 = (start_col - 1) * self.col_width + self.margin
        y1 = (row * self.row_height) - self.row_height + self.margin
        x2 = x1 + (width_cols * self.col_width - (2 * self.margin))
        y2 = y1 + (self.row_height - (2 * self.margin))
        return (x1 + offset, y1 + offset), (x2 + offset, y2 + offset)

    @staticmethod
    def draw_triangle(draw, side_length, middle_point, direction, fill_color):
        """ This function draws a triangle. The triangle is used to indicate the direction of
        a field. The direction is passed as an argument. The direction can be either 'up' or
        'down'."""

        height = math.sqrt(side_length ** 2 - (side_length / 2) ** 2)

        tip = None
        left = None
        right = None
        if direction == "up":
            tip = (middle_point[0], middle_point[1] - height / 2)
            left = (middle_point[0] - side_length / 2, middle_point[1] + height / 2)
            right = (middle_point[0] + side_length / 2, middle_point[1] + height / 2)
        elif direction == "down":
            tip = (middle_point[0], middle_point[1] + height / 2)
            left = (middle_point[0] - side_length / 2, middle_point[1] - height / 2)
            right = (middle_point[0] + side_length / 2, middle_point[1] - height / 2)

        if tip and left and right:
            draw.polygon([tip, left, right], fill=fill_color)

    def draw_field_type_indicator(self, draw, coords, field_type, extra_label=None):
        """ This function draws a small indicator of a field. The indicator
        indicates the type of the field. The field type is passed as an argument."""

        indicator_offset = 2

        # For a list, a dropdown element is rendered. It is indicated by a triangle pointing down.
        if field_type == NdrCoreSearchField.FieldType.LIST:
            triangle_size = self.row_height / 3

            self.draw_triangle(draw, triangle_size,
                               (coords[1][0] - triangle_size + indicator_offset,
                                coords[0][1] + self.row_height / 2 - self.margin + indicator_offset),
                               "down", self.shadow_color)

            self.draw_triangle(draw, triangle_size,
                               (coords[1][0] - triangle_size,
                                coords[0][1] + self.row_height / 2 - self.margin),
                               "down", self.indicator_color)
        # For a number, two triangles are rendered. One pointing up and one pointing down.
        elif field_type == NdrCoreSearchField.FieldType.NUMBER:
            triangle_size = self.row_height / 5

            self.draw_triangle(draw, triangle_size,
                               (coords[1][0] - triangle_size + (indicator_offset / 2),
                                coords[0][1] + self.row_height / 2.5 - self.margin + (indicator_offset / 2)),
                               "up", self.shadow_color)

            self.draw_triangle(draw, triangle_size,
                               (coords[1][0] - triangle_size,
                                coords[0][1] + self.row_height / 2.5 - self.margin),
                               "up", self.indicator_color)

            self.draw_triangle(draw, triangle_size,
                               (coords[1][0] - triangle_size + (indicator_offset / 2),
                                coords[0][1] + 2 * (self.row_height / 3) - self.margin + (indicator_offset / 2)),
                               "down", self.shadow_color)

            self.draw_triangle(draw, triangle_size,
                               (coords[1][0] - triangle_size,
                                coords[0][1] + 2 * (self.row_height / 3) - self.margin),
                               "down", self.indicator_color)
        # For a multi list, a number of selected items is shown. The maximum number of items is 5, it depends
        # on the width of the field how many are shown.
        elif field_type == NdrCoreSearchField.FieldType.MULTI_LIST:
            right_bound = coords[1][0] - 10
            for i in range(5):
                item_right_bound = (self.margin + 60) * (i + 1)
                item_offset = (self.margin + 60) * i
                if coords[0][0] + item_right_bound > right_bound:
                    break

                draw.rounded_rectangle((coords[0][0] + self.margin + item_offset,
                                        coords[0][1] + (self.row_height / 3),
                                        coords[0][0] + self.margin + 60 + item_offset,
                                        coords[0][1] + 2 * (self.row_height / 3)), 3, fill="#CCCCCC")
                draw.text((coords[0][0] + self.margin + 5 + item_offset,
                           coords[0][1] + (self.row_height / 3) + 5), f"Item{(i + 1)} |x", fill=self.text_color)
        # For a boolean, a checkbox is rendered.
        elif field_type == NdrCoreSearchField.FieldType.BOOLEAN:
            draw.rounded_rectangle((coords[0][0] + self.margin + indicator_offset,
                                    coords[0][1] + (self.row_height / 3) + indicator_offset,
                                    coords[0][0] + self.margin + 20 + indicator_offset,
                                    coords[0][1] + 2 * (self.row_height / 3) + indicator_offset), 5,
                                   fill=self.shadow_color)

            draw.rounded_rectangle((coords[0][0] + self.margin,
                                    coords[0][1] + (self.row_height / 3),
                                    coords[0][0] + self.margin + 20,
                                    coords[0][1] + 2 * (self.row_height / 3)), 5, fill=self.field_color)

            draw.text((coords[0][0] + self.margin + 25,
                       coords[0][1] + (self.row_height / 3) + 5),
                      "Yes / No" if extra_label is None else extra_label,
                      fill=self.text_color)

    @staticmethod
    def get_highest_row(data):
        """ This function returns the highest row number"""
        highest_row = 0
        for data_point in data:
            if data_point['row'] > highest_row:
                highest_row = data_point['row']
        return highest_row

    def create_search_form_image_from_raw_data(self, data):
        """ This function creates a form preview image from a list of dictionaries. Each dictionary
        contains the information about a field in the form. The dictionary must contain the following
        keys: 'row', 'col', 'size', 'text' and type. The 'row' key contains the row number of the field. The
        'col' key contains the column number of the field. The 'size' key contains the number of columns
        the field spans. The 'text' key contains the label of the field."""

        self.row_height = 50
        highest_row = self.get_highest_row(data)

        img = Image.new('RGB', ((12 * self.col_width) + self.margin, highest_row * self.row_height + self.margin),
                        color=self.image_background_color)
        draw = ImageDraw.Draw(img)

        for data_point in data:
            coords = self.get_coordinates(data_point['row'], data_point['col'], data_point['size'])
            coords_offset = self.get_coordinates(data_point['row'], data_point['col'], data_point['size'], offset=3)

            if data_point['type'] != NdrCoreSearchField.FieldType.BOOLEAN:
                draw.rounded_rectangle(coords_offset, 5, fill=self.shadow_color, outline="#333333")
                draw.rounded_rectangle(coords, 5, fill=self.field_color, outline="#36454F")
                draw.text((coords[0][0] + 10, coords[0][1] + 5), data_point['text'], (0, 0, 0))
                self.draw_field_type_indicator(draw, coords, data_point['type'])
            else:
                self.draw_field_type_indicator(draw, coords, data_point['type'], extra_label=data_point['text'])

        output = io.BytesIO()
        img.save(output, "PNG")
        return output.getvalue()

    def create_result_card_image_from_raw_data(self, data):
        """ This function creates a result card preview image"""
        highest_row = self.get_highest_row(data)

        img = Image.new('RGB', ((12 * self.col_width) + self.margin, highest_row * self.row_height + self.margin),
                        color=self.image_background_color)
        draw = ImageDraw.Draw(img)

        for data_point in data:
            coords = self.get_coordinates(data_point['row'], data_point['col'], data_point['size'])
            coords_offset = self.get_coordinates(data_point['row'], data_point['col'], data_point['size'], offset=3)
            draw.rounded_rectangle(coords_offset, 5, fill=self.shadow_color, outline="#333333")
            draw.rounded_rectangle(coords, 5, fill=self.field_color, outline="#36454F")
            draw.text((coords[0][0] + 10, coords[0][1] + 5), data_point['text'], (0, 0, 0))

        output = io.BytesIO()
        img.save(output, "PNG")
        return output.getvalue()
