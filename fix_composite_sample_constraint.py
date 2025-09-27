#!/usr/bin/env python
"""
Script para corrigir constraint unique_together de amostras compostas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from quality_control.models import CompositeSample

def fix_composite_sample_constraint():
    """Corrigir constraint unique_together de amostras compostas"""
    
    print("🔧 CORRIGINDO CONSTRAINT DE AMOSTRAS COMPOSTAS")
    print("=" * 60)
    
    try:
        # 1. Aplicar migração para remover constraint
        print("\n1. REMOVENDO CONSTRAINT UNIQUE_TOGETHER:")
        execute_from_command_line(['manage.py', 'migrate', 'quality_control', '0009'])
        print("   ✅ Constraint unique_together removida")
        
        # 2. Aplicar migração para adicionar campo sequence
        print("\n2. ADICIONANDO CAMPO SEQUENCE:")
        execute_from_command_line(['manage.py', 'migrate', 'quality_control', '0010'])
        print("   ✅ Campo sequence adicionado")
        
        # 3. Atualizar sequências das amostras existentes
        print("\n3. ATUALIZANDO SEQUÊNCIAS DAS AMOSTRAS EXISTENTES:")
        samples = CompositeSample.objects.all().order_by('date', 'shift', 'production_line', 'product', 'created_at')
        
        current_sequence = {}
        updated_count = 0
        
        for sample in samples:
            key = f"{sample.date}_{sample.shift_id}_{sample.production_line_id}_{sample.product_id}"
            
            if key not in current_sequence:
                current_sequence[key] = 1
            else:
                current_sequence[key] += 1
            
            sample.sequence = current_sequence[key]
            sample.save(update_fields=['sequence'])
            updated_count += 1
            
            print(f"   - Amostra ID {sample.id}: Sequência {sample.sequence}")
        
        print(f"   ✅ {updated_count} amostras atualizadas")
        
        # 4. Verificar resultado
        print("\n4. VERIFICANDO RESULTADO:")
        samples_by_date = CompositeSample.objects.values('date', 'shift', 'production_line', 'product').distinct()
        print(f"   Combinações únicas de data/turno/linha/produto: {samples_by_date.count()}")
        
        for combo in samples_by_date:
            samples_count = CompositeSample.objects.filter(
                date=combo['date'],
                shift_id=combo['shift'],
                production_line_id=combo['production_line'],
                product_id=combo['product']
            ).count()
            print(f"   - {combo['date']}: {samples_count} amostras")
        
        print("\n✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("   - Constraint unique_together removida")
        print("   - Campo sequence adicionado")
        print("   - Sequências atualizadas")
        print("   - Agora você pode criar múltiplas amostras no mesmo dia")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_composite_sample_constraint()




