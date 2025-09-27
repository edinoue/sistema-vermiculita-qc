#!/usr/bin/env python
"""
Script para configurar propriedades por tipo de análise
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import AnalysisType, Property, AnalysisTypeProperty

def setup_properties_config():
    """Configurar propriedades por tipo de análise"""
    print("=== Configurando Propriedades por Tipo de Análise ===")
    
    try:
        # Obter tipos de análise
        pontual_type = AnalysisType.objects.get(code='PONTUAL')
        composta_type = AnalysisType.objects.get(code='COMPOSTA')
        
        print(f"Tipo Pontual: {pontual_type.name}")
        print(f"Tipo Composta: {composta_type.name}")
        
        # Obter todas as propriedades ativas
        properties = Property.objects.filter(is_active=True)
        print(f"Propriedades encontradas: {properties.count()}")
        
        # Configurar propriedades para análise pontual
        print("\n--- Configurando Análise Pontual ---")
        for property in properties:
            # Propriedades que devem aparecer na análise pontual
            if property.category in ['FISICA', 'QUIMICA', 'GRANULOMETRIA']:
                atp, created = AnalysisTypeProperty.objects.get_or_create(
                    analysis_type=pontual_type,
                    property=property,
                    defaults={'is_required': False}
                )
                if created:
                    print(f"  ✅ {property.name} adicionada à análise pontual")
                else:
                    print(f"  ⚠️  {property.name} já configurada para análise pontual")
        
        # Configurar propriedades para análise composta
        print("\n--- Configurando Análise Composta ---")
        for property in properties:
            # Propriedades que devem aparecer na análise composta
            if property.category in ['FISICA', 'QUIMICA', 'GRANULOMETRIA', 'MINERALOGIA']:
                atp, created = AnalysisTypeProperty.objects.get_or_create(
                    analysis_type=composta_type,
                    property=property,
                    defaults={'is_required': False}
                )
                if created:
                    print(f"  ✅ {property.name} adicionada à análise composta")
                else:
                    print(f"  ⚠️  {property.name} já configurada para análise composta")
        
        # Verificar configurações
        print("\n--- Verificando Configurações ---")
        pontual_properties = Property.objects.filter(
            is_active=True,
            analysistypeproperty__analysis_type=pontual_type
        ).count()
        composta_properties = Property.objects.filter(
            is_active=True,
            analysistypeproperty__analysis_type=composta_type
        ).count()
        
        print(f"Propriedades para análise pontual: {pontual_properties}")
        print(f"Propriedades para análise composta: {composta_properties}")
        
        print("\n=== Configuração concluída! ===")
        
    except AnalysisType.DoesNotExist as e:
        print(f"❌ Tipo de análise não encontrado: {e}")
        print("Execute primeiro: python manage.py migrate")
    except Exception as e:
        print(f"❌ Erro durante a configuração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    setup_properties_config()




