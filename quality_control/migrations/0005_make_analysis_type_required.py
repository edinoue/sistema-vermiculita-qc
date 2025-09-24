# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0004_update_existing_records'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotanalysis',
            name='analysis_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='quality_control.analysistype', verbose_name='Tipo de Análise'),
        ),
    ]
