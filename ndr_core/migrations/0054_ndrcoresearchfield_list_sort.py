from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ndr_core', '0053_ndrcoresearchconfiguration_example_result_json'),
    ]

    operations = [
        migrations.AddField(
            model_name='ndrcoresearchfield',
            name='list_sort',
            field=models.CharField(
                blank=True,
                choices=[('SAVED', 'Saved Order'), ('ALPHA', 'Alphabetical')],
                default='SAVED',
                help_text='Sort order for the dropdown choices',
                max_length=10,
            ),
        ),
    ]