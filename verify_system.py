#!/usr/bin/env python
"""
Script para verificar se o sistema está funcionando
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import AnalysisType, Property, AnalysisTypeProperty, SpotAnalysis
from core.models import ProductionLine, Shift

def verify_system():
    """Verificar se o sistema está funcionando"""
    print("=== Verificando sistema ===")
    
    try:
        # Verificar tipos de análise
        analysis_types = AnalysisType.objects.all()
        print(f"Tipos de análise encontrados: {analysis_types.count()}")
        for at in analysis_types:
            print(f"  - {at.code}: {at.name}")
        
        # Verificar propriedades
        properties = Property.objects.all()
        print(f"Propriedades encontradas: {properties.count()}")
        for prop in properties:
            print(f"  - {prop.identifier}: {prop.name}")
        
        # Verificar configurações de propriedades
        type_properties = AnalysisTypeProperty.objects.all()
        print(f"Configurações de propriedades: {type_properties.count()}")
        for tp in type_properties:
            print(f"  - {tp.analysis_type.code}: {tp.property.identifier}")
        
        # Verificar análises existentes
        analyses = SpotAnalysis.objects.all()
        print(f"Análises existentes: {analyses.count()}")
        
        # Verificar se há análises sem tipo
        analyses_without_type = SpotAnalysis.objects.filter(analysis_type__isnull=True)
        if analyses_without_type.exists():
            print(f"⚠️  {analyses_without_type.count()} análises sem tipo de análise")
        else:
            print("✅ Todas as análises têm tipo definido")
        
        print("\n=== Sistema verificado com sucesso! ===")
        
    except Exception as e:
        print(f"Erro durante a verificação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    verify_system()





