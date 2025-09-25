# Generated manually

from django.db import migrations


def update_existing_analyses(apps, schema_editor):
    SpotAnalysis = apps.get_model('quality_control', 'SpotAnalysis')
    AnalysisType = apps.get_model('quality_control', 'AnalysisType')
    
    # Obter o tipo de análise pontual como padrão
    try:
        default_type = AnalysisType.objects.get(code='PONTUAL')
        
        # Atualizar todos os registros existentes
        SpotAnalysis.objects.filter(analysis_type__isnull=True).update(
            analysis_type=default_type
        )
    except AnalysisType.DoesNotExist:
        # Se não existir, criar o tipo padrão
        default_type = AnalysisType.objects.create(
            code='PONTUAL',
            name='Análise Pontual',
            description='Análises realizadas diretamente no fluxo de produção',
            frequency_per_shift=3,
            is_active=True
        )
        
        # Atualizar todos os registros existentes
        SpotAnalysis.objects.filter(analysis_type__isnull=True).update(
            analysis_type=default_type
        )


def reverse_update_existing_analyses(apps, schema_editor):
    # Não há necessidade de reverter esta operação
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('quality_control', '0003_populate_analysis_types'),
    ]

    operations = [
        migrations.RunPython(update_existing_analyses, reverse_update_existing_analyses),
    ]

