import base64
import io

from PIL import Image, ImageDraw
from django.db.models import Max
from django.http import HttpResponse


def get_coordinates(row, start_col, width_cols):
    col_width = 60
    col_height = 50
    margin = 5

    x1 = (start_col - 1) * col_width + margin
    y1 = (row * col_height) - col_height + margin
    x2 = x1 + (width_cols * col_width - (2 * margin))
    y2 = y1 + (col_height - (2 * margin))

    # return [(x, y), (width, height)]
    return [(x1, y1), (x2, y2)]


def create_img(max_rows):
    img = Image.new('RGB', (720, max_rows * 50), color='#D3D3D3')
    return img


def get_image_from_queryset(search_field_form_configuration_queryset):
    max_row = search_field_form_configuration_queryset.aggregate(Max('field_row'))
    img = create_img(max_row['field_row__max'])
    draw = ImageDraw.Draw(img)

    for field in search_field_form_configuration_queryset:
        coords = get_coordinates(field.field_row, field.field_column, field.field_size)
        draw.rectangle(coords, fill="#FFFFFF", outline="#36454F")
        draw.text((coords[0][0] + 3, coords[0][1] + 3), field.search_field.field_label, (0, 0, 0))

    output = io.BytesIO()
    img.save(output, "PNG")
    img_str = base64.b64encode(output.getvalue())
    return str(img_str.decode("utf-8"))


def get_image_from_raw_data(data):
    highest_row = 0
    for data_point in data:
        if data_point['row'] > highest_row:
            highest_row = data_point['row']
    img = create_img(highest_row)
    draw = ImageDraw.Draw(img)

    for data_point in data:
        coords = get_coordinates(data_point['row'],
                                 data_point['col'],
                                 data_point['size'])
        draw.rectangle(coords, fill="#FFFFFF", outline="#36454F")
        draw.text((coords[0][0] + 3, coords[0][1] + 3), data_point['text'], (0, 0, 0))
    output = io.BytesIO()
    img.save(output, "PNG")
    return output.getvalue()
