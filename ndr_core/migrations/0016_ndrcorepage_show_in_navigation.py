# Generated by Django 4.2 on 2023-08-30 19:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ndr_core", "0015_ndrcorepage_show_page_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="ndrcorepage",
            name="show_in_navigation",
            field=models.BooleanField(
                default=True,
                help_text="Should the page be displayed in the navigation?",
            ),
        ),
    ]