# Generated by Django 4.2.7 on 2024-01-11 17:51

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ndr_core", "0010_ndrcoresearchconfiguration_compact_result_is_default"),
    ]

    operations = [
        migrations.AddField(
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
        migrations.AddField(
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
    ]