# Generated by Django 5.0.2 on 2024-03-07 13:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ndr_core", "0013_remove_ndrcoremanifest_id_ndrcoremanifest_identifier"),
    ]

    operations = [
        migrations.AddField(
            model_name="ndrcoresearchconfiguration",
            name="manifest_page_expression",
            field=models.CharField(blank=True, default=None, max_length=512, null=True),
        ),
    ]