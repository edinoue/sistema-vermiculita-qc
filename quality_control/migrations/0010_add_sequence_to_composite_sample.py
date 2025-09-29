# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0009_remove_composite_sample_unique_constraint'),
    ]

    operations = [
        migrations.AddField(
            model_name='compositesample',
            name='sequence',
            field=models.PositiveIntegerField(default=1, help_text='Número sequencial da amostra no dia', verbose_name='Sequência'),
        ),
    ]





