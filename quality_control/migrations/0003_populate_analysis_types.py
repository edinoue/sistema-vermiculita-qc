# Generated manually

from django.db import migrations


def populate_analysis_types(apps, schema_editor):
    AnalysisType = apps.get_model('quality_control', 'AnalysisType')
    
    # Criar tipos de análise padrão
    AnalysisType.objects.get_or_create(
        code='PONTUAL',
        defaults={
            'name': 'Análise Pontual',
            'description': 'Análises realizadas diretamente no fluxo de produção',
            'frequency_per_shift': 3,
            'is_active': True
        }
    )
    
    AnalysisType.objects.get_or_create(
        code='COMPOSTA',
        defaults={
            'name': 'Análise Composta',
            'description': 'Análises que representam 12 horas de produção',
            'frequency_per_shift': 1,
            'is_active': True
        }
    )


def reverse_populate_analysis_types(apps, schema_editor):
    AnalysisType = apps.get_model('quality_control', 'AnalysisType')
    AnalysisType.objects.filter(code__in=['PONTUAL', 'COMPOSTA']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0002_add_analysis_types'),
    ]

    operations = [
        migrations.RunPython(populate_analysis_types, reverse_populate_analysis_types),
    ]
