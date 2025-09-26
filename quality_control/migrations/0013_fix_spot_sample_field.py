# Generated manually to fix spot_sample field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0012_add_spot_sample_grouping'),
    ]

    operations = [
        # Primeiro, tornar o campo spot_sample nullable temporariamente
        migrations.AlterField(
            model_name='spotanalysis',
            name='spot_sample',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='quality_control.spotsample', verbose_name='Amostra Pontual'),
        ),
    ]
