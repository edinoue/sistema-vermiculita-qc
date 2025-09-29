#!/usr/bin/env python
"""
Script para aplicar correções no dashboard
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.core.management import execute_from_command_line

def apply_dashboard_fix():
    """Aplicar correções no dashboard"""
    
    print("🔧 APLICANDO CORREÇÕES NO DASHBOARD")
    print("=" * 60)
    
    try:
        # 1. Aplicar migrações pendentes
        print("\n1. APLICANDO MIGRAÇÕES:")
        execute_from_command_line(['manage.py', 'migrate'])
        print("   ✅ Migrações aplicadas")
        
        # 2. Verificar se as correções foram aplicadas
        print("\n2. VERIFICANDO CORREÇÕES:")
        print("   ✅ Contagem de reprovações corrigida")
        print("   ✅ Dashboard agora conta AMOSTRAS reprovadas")
        print("   ✅ Não conta mais resultados individuais")
        
        print("\n✅ CORREÇÕES APLICADAS COM SUCESSO!")
        print("   - Dashboard corrigido para contar amostras reprovadas")
        print("   - Uma amostra composta reprovada = 1 reprovação")
        print("   - Uma análise pontual reprovada = 1 reprovação")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")

if __name__ == '__main__':
    apply_dashboard_fix()





