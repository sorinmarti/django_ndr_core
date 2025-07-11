# pylint: skip-file
# Generated by Django 4.2.7 on 2023-11-19 21:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "ndr_core",
            "0005_alter_ndrcoreresultfieldcardconfiguration_field_column_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="ndrcoreresultfield",
            name="field_classes",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Bootstrap classes to apply to the display.",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="ndrcoreresultfield",
            name="field_type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "String"),
                    (2, "Rich Text String"),
                    (3, "Image"),
                    (4, "IIIF Image"),
                    (5, "Table"),
                    (6, "Map"),
                    (7, "List"),
                ],
                default=1,
                help_text="Type of the display field",
            ),
        ),
    ]
