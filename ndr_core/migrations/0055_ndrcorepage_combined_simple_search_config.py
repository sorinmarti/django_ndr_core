from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ndr_core', '0054_ndrcoresearchfield_list_sort'),
    ]

    operations = [
        migrations.AddField(
            model_name='ndrcorepage',
            name='combined_simple_search_config',
            field=models.ForeignKey(
                blank=True,
                help_text='Master config for the combined simple search tab. When set, replaces the individual per-config simple search tabs with one unified tab that queries all configs simultaneously.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='combined_master_for',
                to='ndr_core.ndrcoresearchconfiguration',
            ),
        ),
    ]