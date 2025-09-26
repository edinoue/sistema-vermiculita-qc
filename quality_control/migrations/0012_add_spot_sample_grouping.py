# Generated manually for spot sample grouping

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.core.validators
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0011_remove_spot_analysis_unique_constraint'),
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SpotSample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('date', models.DateField(verbose_name='Data')),
                ('sequence', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(3)], verbose_name='Sequência')),
                ('sample_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Horário da Amostra')),
                ('status', models.CharField(choices=[('APPROVED', 'Aprovado'), ('ALERT', 'Alerta'), ('REJECTED', 'Reprovado')], default='PENDENTE', max_length=20, verbose_name='Status')),
                ('observations', models.TextField(blank=True, verbose_name='Observações')),
                ('analysis_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='quality_control.analysistype', verbose_name='Tipo de Análise')),
                ('operator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Operador')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='quality_control.product', verbose_name='Produto')),
                ('production_line', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.productionline', verbose_name='Linha de Produção')),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.shift', verbose_name='Turno')),
            ],
            options={
                'verbose_name': 'Amostra Pontual',
                'verbose_name_plural': 'Amostras Pontuais',
                'ordering': ['-date', '-sample_time'],
            },
        ),
        migrations.AddConstraint(
            model_name='spotsample',
            constraint=models.UniqueConstraint(fields=('date', 'shift', 'production_line', 'product', 'sequence'), name='unique_spot_sample'),
        ),
        migrations.AddField(
            model_name='spotanalysis',
            name='spot_sample',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='quality_control.spotsample', verbose_name='Amostra Pontual'),
        ),
        migrations.AlterField(
            model_name='spotanalysis',
            name='property',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='quality_control.property', verbose_name='Propriedade'),
        ),
        migrations.AlterField(
            model_name='spotanalysis',
            name='status',
            field=models.CharField(choices=[('APPROVED', 'Aprovado'), ('ALERT', 'Alerta'), ('REJECTED', 'Reprovado')], max_length=20, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='spotanalysis',
            name='value',
            field=models.DecimalField(decimal_places=4, max_digits=10, verbose_name='Valor'),
        ),
        migrations.AddConstraint(
            model_name='spotanalysis',
            constraint=models.UniqueConstraint(fields=('spot_sample', 'property'), name='unique_spot_analysis_per_sample'),
        ),
    ]
