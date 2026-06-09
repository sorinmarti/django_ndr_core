from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ndr_core', '0055_ndrcorepage_combined_simple_search_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='ndrcoresearchfield',
            name='show_label',
            field=models.BooleanField(default=True, help_text='Show the field label in the search form. Uncheck to render the field without a label.'),
        ),
    ]