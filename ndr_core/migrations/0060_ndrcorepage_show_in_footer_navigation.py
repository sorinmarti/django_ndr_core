from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ndr_core', '0059_card_width'),
    ]

    operations = [
        migrations.AddField(
            model_name='ndrcorepage',
            name='show_in_footer_navigation',
            field=models.BooleanField(
                default=True,
                help_text='Should the page be displayed in the footer navigation?'
            ),
        ),
    ]
