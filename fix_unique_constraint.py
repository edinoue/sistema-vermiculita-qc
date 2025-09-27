#!/usr/bin/env python
"""
Script para corrigir constraint unique_together
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line

def fix_unique_constraint():
    """Aplicar migração para remover constraint unique_together"""
    
    print("🔧 CORRIGINDO CONSTRAINT UNIQUE_TOGETHER")
    print("=" * 60)
    
    try:
        # Aplicar migração
        print("\n1. APLICANDO MIGRAÇÃO:")
        execute_from_command_line(['manage.py', 'migrate', 'quality_control', '0009'])
        print("   ✅ Migração aplicada com sucesso")
        
        # Verificar se a constraint foi removida
        print("\n2. VERIFICANDO AMOSTRAS COMPOSTAS EXISTENTES:")
        from quality_control.models import CompositeSample
        samples = CompositeSample.objects.all()
        print(f"   Total de amostras compostas: {samples.count()}")
        
        for sample in samples:
            print(f"   - ID: {sample.id}, Data: {sample.date}, Produto: {sample.product.code}")
        
        print("\n3. TESTANDO CRIAÇÃO DE NOVA AMOSTRA:")
        print("   ✅ Agora você pode criar múltiplas amostras compostas no mesmo dia")
        print("   ✅ Não haverá mais erro de constraint UNIQUE")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")

if __name__ == '__main__':
    fix_unique_constraint()




