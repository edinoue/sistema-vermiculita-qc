#!/usr/bin/env python
"""
Script para testar dados do turno atual
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.utils import timezone
from quality_control.models import SpotSample, SpotAnalysis
from core.models import Shift
import pytz

def test_current_shift_data():
    """Testar dados do turno atual"""
    print("🔍 === TESTE DADOS TURNO ATUAL ===")
    
    # Obter horário correto do Brasil
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    current_time_brazil = timezone.now().astimezone(brazil_tz)
    today = timezone.now().date()
    
    print(f"📅 Data atual: {today}")
    print(f"🕐 Horário UTC: {timezone.now()}")
    print(f"🕐 Horário Brasil: {current_time_brazil}")
    print(f"🕐 Hora Brasil: {current_time_brazil.hour}")
    
    # Determinar turno atual
    current_shift = None
    if 7 <= current_time_brazil.hour < 19:
        current_shift = Shift.objects.filter(name='A').first()
        print(f"🔍 Turno atual: A (7h-19h)")
    else:
        current_shift = Shift.objects.filter(name='B').first()
        print(f"🔍 Turno atual: B (19h-7h)")
    
    if not current_shift:
        print("❌ Nenhum turno encontrado!")
        return
    
    print(f"✅ Turno encontrado: {current_shift.name}")
    
    # Buscar amostras do turno atual
    current_samples = SpotSample.objects.filter(
        date=today,
        shift=current_shift
    ).select_related(
        'product', 'production_line', 'production_line__plant', 'shift'
    ).order_by('production_line', 'product', '-sample_sequence')
    
    print(f"📊 Amostras do turno atual: {current_samples.count()}")
    
    if current_samples.exists():
        print("✅ HÁ dados do turno atual!")
        for sample in current_samples:
            print(f"  - {sample.product.name} - {sample.production_line.name} - Seq: {sample.sample_sequence}")
            analyses = SpotAnalysis.objects.filter(spot_sample=sample)
            print(f"    Análises: {analyses.count()}")
            for analysis in analyses:
                print(f"      {analysis.property.name}: {analysis.value} {analysis.property.unit} ({analysis.status})")
    else:
        print("❌ NÃO há dados do turno atual")
        
        # Verificar outros turnos
        print("\n🔍 Verificando outros turnos:")
        all_today_samples = SpotSample.objects.filter(date=today)
        print(f"  Total de amostras hoje: {all_today_samples.count()}")
        
        for sample in all_today_samples:
            print(f"  - Turno: {sample.shift.name} - {sample.product.name} - {sample.production_line.name}")
    
    print("\n✅ Teste concluído!")

if __name__ == '__main__':
    test_current_shift_data()
