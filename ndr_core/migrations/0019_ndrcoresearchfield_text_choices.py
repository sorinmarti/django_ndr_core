# Generated by Django 5.0.4 on 2024-04-09 11:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ndr_core", "0018_alter_ndrcoresearchfield_api_parameter_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ndrcoresearchfield",
            name="text_choices",
            field=models.TextField(
                blank=True, default="", help_text="Used for infor text"
            ),
        ),
    ]