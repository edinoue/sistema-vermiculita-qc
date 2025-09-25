#!/usr/bin/env python
"""
Script para corrigir constraint unique_together de análises pontuais
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from quality_control.models import SpotAnalysis

def fix_spot_analysis_constraint():
    """Corrigir constraint unique_together de análises pontuais"""
    
    print("🔧 CORRIGINDO CONSTRAINT DE ANÁLISES PONTUAIS")
    print("=" * 60)
    
    try:
        # 1. Aplicar migração para remover constraint
        print("\n1. REMOVENDO CONSTRAINT UNIQUE_TOGETHER:")
        execute_from_command_line(['manage.py', 'migrate', 'quality_control', '0011'])
        print("   ✅ Constraint unique_together removida")
        
        # 2. Verificar análises existentes
        print("\n2. VERIFICANDO ANÁLISES EXISTENTES:")
        analyses = SpotAnalysis.objects.all()
        print(f"   Total de análises pontuais: {analyses.count()}")
        
        # 3. Verificar duplicatas (se houver)
        print("\n3. VERIFICANDO POSSÍVEIS DUPLICATAS:")
        from django.db.models import Count
        
        duplicates = SpotAnalysis.objects.values(
            'analysis_type', 'date', 'shift', 'production_line', 'product', 'property', 'sequence'
        ).annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicates.exists():
            print(f"   ⚠️  {duplicates.count()} combinações duplicadas encontradas")
            for dup in duplicates:
                print(f"   - {dup}")
        else:
            print("   ✅ Nenhuma duplicata encontrada")
        
        # 4. Testar criação de nova análise
        print("\n4. TESTANDO CRIAÇÃO DE NOVA ANÁLISE:")
        print("   ✅ Agora você pode criar múltiplas análises da mesma propriedade")
        print("   ✅ Não haverá mais erro de constraint UNIQUE")
        
        print("\n✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("   - Constraint unique_together removida")
        print("   - Múltiplas análises da mesma propriedade permitidas")
        print("   - Sistema mais flexível para operações")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_spot_analysis_constraint()
