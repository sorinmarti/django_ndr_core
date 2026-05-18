from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ndr_core', '0052_ndrcoreuielement_card_grid_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='ndrcoresearchconfiguration',
            name='example_result_json',
            field=models.JSONField(
                blank=True,
                null=True,
                verbose_name='Example Result JSON',
                help_text='Paste a single example API result record here. Used to suggest field paths and preview result fields.'
            ),
        ),
    ]