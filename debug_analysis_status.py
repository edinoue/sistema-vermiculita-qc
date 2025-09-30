#!/usr/bin/env python
"""
Script para debugar o status das análises pontuais
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models_production import SpotAnalysisRegistration
from quality_control.models import Specification, Product, Property

def debug_analysis_status():
    """Debugar status das análises pontuais"""
    
    print("🔍 DEBUGANDO STATUS DAS ANÁLISES PONTUAIS")
    print("=" * 50)
    
    # 1. Verificar análises existentes
    analyses = SpotAnalysisRegistration.objects.all()
    print(f"\n📊 Análises encontradas: {analyses.count()}")
    
    for analysis in analyses:
        print(f"\n🔬 Análise ID: {analysis.id}")
        print(f"   Produto: {analysis.product.name}")
        print(f"   Status atual: {analysis.analysis_result}")
        print(f"   Pontual: {analysis.pontual_number}")
        
        # Verificar especificações do produto
        specs = Specification.objects.filter(product=analysis.product, is_active=True)
        print(f"   Especificações encontradas: {specs.count()}")
        
        for spec in specs:
            print(f"      - {spec.property.identifier}: LSL={spec.lsl}, USL={spec.usl}")
        
        # Verificar resultados das propriedades
        results = analysis.property_results.all()
        print(f"   Resultados de propriedades: {results.count()}")
        
        for result in results:
            print(f"      - {result.property.identifier}: {result.value} {result.unit}")
            
            # Verificar se há especificação para esta propriedade
            spec = specs.filter(property=result.property).first()
            if spec:
                print(f"        Especificação: LSL={spec.lsl}, USL={spec.usl}")
                if spec.lsl and result.value < spec.lsl:
                    print(f"        ❌ ABAIXO DO LIMITE INFERIOR!")
                elif spec.usl and result.value > spec.usl:
                    print(f"        ❌ ACIMA DO LIMITE SUPERIOR!")
                else:
                    print(f"        ✅ DENTRO DOS LIMITES")
            else:
                print(f"        ⚠️ SEM ESPECIFICAÇÃO")
        
        # Testar cálculo do status
        calculated_status = analysis.calculate_analysis_result()
        print(f"   Status calculado: {calculated_status}")
        
        if analysis.analysis_result != calculated_status:
            print(f"   🔄 ATUALIZANDO STATUS: {analysis.analysis_result} → {calculated_status}")
            analysis.analysis_result = calculated_status
            analysis.save()
        else:
            print(f"   ✅ Status já está correto")

if __name__ == '__main__':
    debug_analysis_status()
