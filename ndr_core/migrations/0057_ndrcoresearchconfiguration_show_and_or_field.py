from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ndr_core', '0056_ndrcoresearchfield_show_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='ndrcoresearchconfiguration',
            name='show_and_or_field',
            field=models.BooleanField(default=True, help_text='Show the AND / OR search toggle in the simple search tab.'),
        ),
    ]