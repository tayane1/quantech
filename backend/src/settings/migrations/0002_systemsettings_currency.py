# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemsettings',
            name='currency',
            field=models.CharField(default='XOF', help_text='Code devise ISO 4217 (ex: XOF, EUR, USD)', max_length=3),
        ),
    ]

