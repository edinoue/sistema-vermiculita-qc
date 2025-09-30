#!/usr/bin/env python
"""
Script para corrigir status de amostras compostas existentes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models import CompositeSample, CompositeSampleResult

def fix_composite_sample_status():
    """Corrigir status de amostras compostas existentes"""
    
    print("🔧 CORRIGINDO STATUS DE AMOSTRAS COMPOSTAS")
    print("=" * 60)
    
    # 1. Verificar amostras compostas existentes
    print("\n1. VERIFICANDO AMOSTRAS COMPOSTAS EXISTENTES:")
    samples = CompositeSample.objects.all()
    print(f"   Total de amostras compostas: {samples.count()}")
    
    corrected_count = 0
    
    for sample in samples:
        old_status = sample.status
        print(f"\n   Amostra ID {sample.id} ({sample.date}):")
        print(f"      Status atual: {old_status}")
        
        # Verificar resultados
        results = CompositeSampleResult.objects.filter(composite_sample=sample)
        print(f"      Resultados: {results.count()}")
        
        for result in results:
            print(f"        - {result.property.identifier}: {result.value} ({result.status})")
        
        # Calcular novo status
        new_status = sample.calculate_overall_status()
        print(f"      Status calculado: {new_status}")
        
        # Atualizar se necessário
        if old_status != new_status:
            sample.status = new_status
            sample.save(update_fields=['status'])
            print(f"      🔄 Status atualizado: {old_status} → {new_status}")
            corrected_count += 1
        else:
            print(f"      ✅ Status já está correto")
    
    print(f"\n✅ {corrected_count} amostras compostas corrigidas")
    
    # 2. Verificar regras de status
    print("\n2. VERIFICANDO REGRAS DE STATUS:")
    print("   - Se qualquer resultado for REJECTED → amostra REJECTED")
    print("   - Se qualquer resultado for ALERT → amostra ALERT")
    print("   - Se todos os resultados forem APPROVED → amostra APPROVED")
    
    # 3. Exemplos de amostras com diferentes status
    print("\n3. EXEMPLOS DE STATUS:")
    
    rejected_samples = CompositeSample.objects.filter(status='REJECTED')
    approved_samples = CompositeSample.objects.filter(status='APPROVED')
    
    print(f"   Amostras rejeitadas: {rejected_samples.count()}")
    print(f"   Amostras aprovadas: {approved_samples.count()}")
    
    # Mostrar exemplo de amostra rejeitada
    if rejected_samples.exists():
        sample = rejected_samples.first()
        print(f"\n   Exemplo de amostra rejeitada (ID {sample.id}):")
        results = CompositeSampleResult.objects.filter(composite_sample=sample)
        for result in results:
            status_icon = "❌" if result.status == 'REJECTED' else "✅"
            print(f"      {status_icon} {result.property.identifier}: {result.value} ({result.status})")

if __name__ == '__main__':
    fix_composite_sample_status()






