from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ndr_core', '0047_ndrcorepage_image_opacity'),
    ]

    operations = [
        migrations.AddField(
            model_name='ndrcoresearchconfiguration',
            name='api_settings',
            field=models.JSONField(
                blank=True,
                default=dict,
                verbose_name='API Settings',
                help_text='API-type-specific settings stored as JSON. Managed via the form.',
            ),
        ),
    ]