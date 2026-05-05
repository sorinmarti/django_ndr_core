from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ndr_core', '0051_remove_compact_page_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='ndrcoreuielement',
            name='card_grid_columns',
            field=models.CharField(
                choices=[('slim', 'Slim (6 per row on large screens)'),
                         ('normal', 'Normal (4 per row on large screens)'),
                         ('wide', 'Wide (3 per row on large screens)')],
                default='normal',
                help_text='Card width in the grid. Applies only to Card Grid elements.',
                max_length=10,
            ),
        ),
    ]