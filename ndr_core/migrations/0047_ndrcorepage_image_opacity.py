from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ndr_core', '0046_alter_ndrcoreuielement_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='ndrcorepage',
            name='image_opacity',
            field=models.FloatField(
                default=1.0,
                validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                help_text='Background image opacity (0.0 = invisible, 1.0 = fully visible)',
            ),
        ),
    ]
