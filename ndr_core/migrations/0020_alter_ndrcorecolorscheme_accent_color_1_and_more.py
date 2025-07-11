# Generated by Django 5.0.4 on 2024-04-15 11:43

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ndr_core", "0019_ndrcoresearchfield_text_choices"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="accent_color_1",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Accent color 1. Used as navigation background and the like.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="accent_color_2",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Accent color 2. Used as element background and the like.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="background_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Basic background color of the whole page.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="button_border_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Border color of primary buttons.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="button_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Background color of primary buttons.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="button_hover_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Hover color of primary buttons.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="button_text_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Text color of primary buttons.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="container_bg_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Basic container (cards, tables, etc.) color of the whole page.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="error_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Error color for alerts.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="footer_bg",
            field=colorfield.fields.ColorField(
                default="#FFFFFF", image_field=None, max_length=25, samples=None
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="footer_link_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF", image_field=None, max_length=25, samples=None
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="footer_link_hover_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF", image_field=None, max_length=25, samples=None
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="form_field_bg",
            field=colorfield.fields.ColorField(
                default="#FFFFFF", image_field=None, max_length=25, samples=None
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="form_field_fg",
            field=colorfield.fields.ColorField(
                default="#FFFFFF", image_field=None, max_length=25, samples=None
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="info_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Info color for alerts.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="link_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Color for links.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="nav_active_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Color for active navigation links.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="nav_link_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Color navigation for links.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="powered_by_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF", image_field=None, max_length=25, samples=None
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="second_button_border_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Border color of secondary buttons.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="second_button_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Background color of secondary buttons.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="second_button_hover_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Hover color of secondary buttons.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="second_button_text_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Text color of secondary buttons.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="success_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Success color for alerts.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="tab_active_title_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Color for active tab titles.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="tab_title_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Color for tab titles.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="text_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Basic text color for the whole page.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcorecolorscheme",
            name="title_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Title text color for the whole page.",
                image_field=None,
                max_length=25,
                samples=None,
            ),
        ),
    ]
