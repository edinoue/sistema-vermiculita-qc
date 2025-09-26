# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nome')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='Código')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('frequency_per_shift', models.PositiveIntegerField(default=1, verbose_name='Frequência por Turno')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Tipo de Análise',
                'verbose_name_plural': 'Tipos de Análise',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='AnalysisTypeProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analysis_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quality_control.analysistype', verbose_name='Tipo de Análise')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quality_control.property', verbose_name='Propriedade')),
                ('is_required', models.BooleanField(default=False, verbose_name='Obrigatório')),
                ('display_order', models.PositiveIntegerField(default=0, verbose_name='Ordem de Exibição')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Propriedade do Tipo de Análise',
                'verbose_name_plural': 'Propriedades dos Tipos de Análise',
                'ordering': ['display_order', 'property__name'],
            },
        ),
        migrations.AddField(
            model_name='spotanalysis',
            name='analysis_type',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.PROTECT, to='quality_control.analysistype', verbose_name='Tipo de Análise'),
        ),
        migrations.AlterUniqueTogether(
            name='analysistypeproperty',
            unique_together={('analysis_type', 'property')},
        ),
        migrations.AlterUniqueTogether(
            name='spotanalysis',
            unique_together={('analysis_type', 'date', 'shift', 'production_line', 'product', 'property', 'sequence')},
        ),
    ]



