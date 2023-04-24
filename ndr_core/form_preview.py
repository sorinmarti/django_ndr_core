"""This module contains functions to create a preview image of a form."""
import io
import math
from PIL import Image, ImageDraw
from ndr_core.models import NdrCoreSearchField

col_width = 60                      # Width of a column in pixels. Maximum of columns is 12.
row_height = 50                     # Height of a row in pixels. Maximum of rows is 20.
margin = 5                          # Margin of a field in pixels.

shadow_color = "#444444"            # Color of the shadow
indicator_color = "#666666"         # Color of the field type indicator
image_background_color = '#D3D3D3'  # Color of the background of the image
field_color = "#FFFFFF"             # Color of the field
text_color = "#000000"              # Color of the text


def get_coordinates(row, start_col, width_cols, offset=0):
    """ A form is organized in rows and columns. This function returns the coordinates of a rectangle
    that represents a field in the form. The coordinates are returned as a list of tuples. The first
    tuple contains the coordinates of the top left corner of the rectangle. The second tuple contains
    the bottom right corner of the rectangle. The coordinates are in pixels."""

    x1 = (start_col - 1) * col_width + margin
    y1 = (row * row_height) - row_height + margin
    x2 = x1 + (width_cols * col_width - (2 * margin))
    y2 = y1 + (row_height - (2 * margin))
    return (x1+offset, y1+offset), (x2+offset, y2+offset)


def draw_triangle(draw, side_length, middle_point, direction, fill_color):
    """ This function draws a triangle. The triangle is used to indicate the direction of a field.
    The direction is passed as an argument. The direction can be either 'up' or 'down'."""

    height = math.sqrt(side_length ** 2 - (side_length / 2) ** 2)

    tip = None
    left = None
    right = None
    if direction == "up":
        tip = (middle_point[0], middle_point[1] - height/2)
        left = (middle_point[0] - side_length/2, middle_point[1] + height/2)
        right = (middle_point[0] + side_length/2, middle_point[1] + height/2)
    elif direction == "down":
        tip = (middle_point[0], middle_point[1] + height/2)
        left = (middle_point[0] - side_length/2, middle_point[1] - height/2)
        right = (middle_point[0] + side_length/2, middle_point[1] - height/2)

    if tip and left and right:
        draw.polygon([tip, left, right], fill=fill_color)


def draw_field_type_indicator(draw, coords, field_type, extra_label=None):
    """ This function draws a small indicator of a field. The indicator
    indicates the type of the field. The field type is passed as an argument."""

    indicator_offset = 2

    # For a list, a dropdown element is rendered. It is indicated by a triangle pointing down.
    if field_type == NdrCoreSearchField.FieldType.LIST:
        triangle_size = row_height/3

        draw_triangle(draw, triangle_size,
                      (coords[1][0] - triangle_size + indicator_offset,
                       coords[0][1] + row_height/2 - margin + indicator_offset),
                      "down", shadow_color)

        draw_triangle(draw, triangle_size,
                      (coords[1][0] - triangle_size,
                       coords[0][1] + row_height/2 - margin),
                      "down", indicator_color)
    # For a number, two triangles are rendered. One pointing up and one pointing down.
    elif field_type == NdrCoreSearchField.FieldType.NUMBER:
        triangle_size = row_height / 5

        draw_triangle(draw, triangle_size,
                      (coords[1][0] - triangle_size + (indicator_offset/2),
                       coords[0][1] + row_height / 2.5 - margin + (indicator_offset/2)),
                      "up", shadow_color)

        draw_triangle(draw, triangle_size,
                      (coords[1][0] - triangle_size,
                       coords[0][1] + row_height / 2.5 - margin),
                      "up", indicator_color)

        draw_triangle(draw, triangle_size,
                      (coords[1][0] - triangle_size + (indicator_offset/2),
                       coords[0][1] + 2*(row_height / 3) - margin + (indicator_offset/2)),
                      "down", shadow_color)

        draw_triangle(draw, triangle_size,
                      (coords[1][0] - triangle_size,
                       coords[0][1] + 2*(row_height / 3) - margin),
                      "down", indicator_color)
    # For a multi list, a number of selected items is shown. The maximum number of items is 5, it depends
    # on the width of the field how many are shown.
    elif field_type == NdrCoreSearchField.FieldType.MULTI_LIST:
        right_bound = coords[1][0] - 10
        for i in range(5):
            item_right_bound = (margin + 60) * (i+1)
            item_offset = (margin + 60) * i
            if coords[0][0] + item_right_bound > right_bound:
                break

            draw.rounded_rectangle((coords[0][0] + margin + item_offset,
                                    coords[0][1] + (row_height/3),
                                    coords[0][0] + margin + 60 + item_offset,
                                    coords[0][1] + 2*(row_height/3)), 3, fill="#CCCCCC")
            draw.text((coords[0][0] + margin + 5 + item_offset,
                       coords[0][1] + (row_height/3) + 5), f"Item{(i+1)} |x", fill=text_color)
    # For a boolean, a checkbox is rendered.
    elif field_type == NdrCoreSearchField.FieldType.BOOLEAN:
        draw.rounded_rectangle((coords[0][0] + margin + indicator_offset,
                                coords[0][1] + (row_height / 3) + indicator_offset,
                                coords[0][0] + margin + 20 + indicator_offset,
                                coords[0][1] + 2 * (row_height / 3) + indicator_offset), 5, fill=shadow_color)

        draw.rounded_rectangle((coords[0][0] + margin,
                                coords[0][1] + (row_height/3),
                                coords[0][0] + margin + 20,
                                coords[0][1] + 2*(row_height/3)), 5, fill=field_color)

        draw.text((coords[0][0] + margin + 25,
                   coords[0][1] + (row_height/3) + 5),
                  "Yes / No" if extra_label is None else extra_label,
                  fill=text_color)


def get_image_from_raw_data(data):
    """ This function creates a form preview image from a list of dictionaries. Each dictionary
    contains the information about a field in the form. The dictionary must contain the following
    keys: 'row', 'col', 'size', 'text' and type. The 'row' key contains the row number of the field. The
    'col' key contains the column number of the field. The 'size' key contains the number of columns
    the field spans. The 'text' key contains the label of the field."""

    highest_row = 0
    for data_point in data:
        if data_point['row'] > highest_row:
            highest_row = data_point['row']

    img = Image.new('RGB', ((12*col_width) + margin, highest_row * row_height + margin), color=image_background_color)
    draw = ImageDraw.Draw(img)

    for data_point in data:
        coords = get_coordinates(data_point['row'], data_point['col'], data_point['size'])
        coords_offset = get_coordinates(data_point['row'], data_point['col'], data_point['size'], offset=3)

        if data_point['type'] != NdrCoreSearchField.FieldType.BOOLEAN:
            draw.rounded_rectangle(coords_offset, 5, fill=shadow_color, outline="#333333")
            draw.rounded_rectangle(coords, 5, fill=field_color, outline="#36454F")
            draw.text((coords[0][0] + 10, coords[0][1] + 5), data_point['text'], (0, 0, 0))
            draw_field_type_indicator(draw, coords, data_point['type'])
        else:
            draw_field_type_indicator(draw, coords, data_point['type'], extra_label=data_point['text'])

    output = io.BytesIO()
    img.save(output, "PNG")
    return output.getvalue()
