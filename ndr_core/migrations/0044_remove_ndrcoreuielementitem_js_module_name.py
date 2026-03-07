# Generated manually to remove unused js_module_name field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ndr_core', '0043_ndrcoreuielementitem_js_module_config_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ndrcoreuielementitem',
            name='js_module_name',
        ),
    ]
