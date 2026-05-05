from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ndr_core', '0050_alter_ndrcoresearchconfiguration_simple_query_main_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ndrcoresearchconfiguration',
            name='compact_page_size',
        ),
    ]