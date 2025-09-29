#!/usr/bin/env python
"""
Script para recalcular o status das análises pontuais existentes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from quality_control.models_production import SpotAnalysisRegistration

def recalculate_analysis_status():
    """Recalcular status das análises pontuais existentes"""
    
    print("🔧 Recalculando status das análises pontuais...")
    
    analyses = SpotAnalysisRegistration.objects.all()
    print(f"📊 Encontradas {analyses.count()} análises")
    
    approved_count = 0
    rejected_count = 0
    pending_count = 0
    
    for analysis in analyses:
        old_status = analysis.analysis_result
        new_status = analysis.calculate_analysis_result()
        
        if old_status != new_status:
            analysis.analysis_result = new_status
            analysis.save()
            print(f"🔄 Análise {analysis.id}: {old_status} → {new_status}")
        
        if new_status == 'APPROVED':
            approved_count += 1
        elif new_status == 'REJECTED':
            rejected_count += 1
        else:
            pending_count += 1
    
    print(f"\n✅ Status recalculado com sucesso!")
    print(f"   ✅ Aprovadas: {approved_count}")
    print(f"   ❌ Reprovadas: {rejected_count}")
    print(f"   ⏳ Pendentes: {pending_count}")

if __name__ == '__main__':
    recalculate_analysis_status()
