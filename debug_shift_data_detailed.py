#!/usr/bin/env python
"""
Script para debugar dados por turno de forma detalhada
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

def debug_shift_data_detailed():
    """Debugar dados por turno de forma detalhada"""
    print("🔍 === DEBUG SHIFT DATA DETAILED ===")
    
    # Obter horário correto do Brasil
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    current_time_brazil = timezone.now().astimezone(brazil_tz)
    today = timezone.now().date()
    
    print(f"📅 Data atual: {today}")
    print(f"🕐 Horário UTC: {timezone.now()}")
    print(f"🕐 Horário Brasil: {current_time_brazil}")
    print(f"🕐 Hora Brasil: {current_time_brazil.hour}")
    
    # 1. Verificar turnos disponíveis
    print("\n1️⃣ Turnos disponíveis:")
    shifts = Shift.objects.all()
    for shift in shifts:
        print(f"  - {shift.name}: {shift.start_time} - {shift.end_time}")
    
    # 2. Determinar turno atual
    current_shift = None
    if 7 <= current_time_brazil.hour < 19:
        current_shift = Shift.objects.filter(name='A').first()
        print(f"\n2️⃣ Turno atual detectado: A (7h-19h)")
    else:
        current_shift = Shift.objects.filter(name='B').first()
        print(f"\n2️⃣ Turno atual detectado: B (19h-7h)")
    
    if current_shift:
        print(f"  Turno encontrado: {current_shift.name}")
    else:
        print("  ❌ Nenhum turno encontrado!")
    
    # 3. Verificar TODAS as amostras
    print("\n3️⃣ TODAS as amostras no sistema:")
    all_samples = SpotSample.objects.all()
    print(f"  Total: {all_samples.count()}")
    
    for sample in all_samples:
        print(f"    - {sample.date} - Turno: {sample.shift.name} - {sample.product.name} - {sample.production_line.name}")
    
    # 4. Verificar amostras por turno hoje
    print("\n4️⃣ Amostras por turno hoje:")
    for shift in shifts:
        samples = SpotSample.objects.filter(date=today, shift=shift)
        print(f"  Turno {shift.name}: {samples.count()} amostras")
        
        for sample in samples:
            print(f"    - {sample.product.name} - {sample.production_line.name} - Seq: {sample.sample_sequence}")
            analyses = SpotAnalysis.objects.filter(spot_sample=sample)
            print(f"      Análises: {analyses.count()}")
            for analysis in analyses:
                print(f"        {analysis.property.name}: {analysis.value} {analysis.property.unit} ({analysis.status})")
    
    # 5. Verificar amostras do turno atual
    if current_shift:
        print(f"\n5️⃣ Amostras do turno atual ({current_shift.name}):")
        current_samples = SpotSample.objects.filter(date=today, shift=current_shift)
        print(f"  Total: {current_samples.count()}")
        
        for sample in current_samples:
            print(f"    - {sample.product.name} - {sample.production_line.name} - Seq: {sample.sample_sequence}")
            analyses = SpotAnalysis.objects.filter(spot_sample=sample)
            print(f"      Análises: {analyses.count()}")
    else:
        print("\n5️⃣ Nenhum turno atual definido")
    
    # 6. Verificar amostras de outros turnos
    print("\n6️⃣ Amostras de outros turnos hoje:")
    other_samples = SpotSample.objects.filter(date=today).exclude(shift=current_shift) if current_shift else SpotSample.objects.filter(date=today)
    print(f"  Total: {other_samples.count()}")
    
    for sample in other_samples:
        print(f"    - Turno: {sample.shift.name} - {sample.product.name} - {sample.production_line.name}")
    
    # 7. Verificar se há dados de outras datas
    print("\n7️⃣ Amostras de outras datas:")
    other_dates = SpotSample.objects.exclude(date=today).order_by('-date')[:10]
    print(f"  Total: {other_dates.count()}")
    
    for sample in other_dates:
        print(f"    - {sample.date} - Turno: {sample.shift.name} - {sample.product.name}")
    
    # 8. Verificar análises
    print("\n8️⃣ TODAS as análises:")
    all_analyses = SpotAnalysis.objects.all()
    print(f"  Total: {all_analyses.count()}")
    
    for analysis in all_analyses[:10]:  # Mostrar apenas 10
        print(f"    - {analysis.spot_sample.date} - Turno: {analysis.spot_sample.shift.name} - {analysis.property.name}: {analysis.value} ({analysis.status})")
    
    # 9. Sugestão de solução
    print("\n9️⃣ Sugestão de solução:")
    if current_samples.count() == 0:
        print("  ❌ Nenhuma amostra do turno atual encontrada")
        if other_samples.count() > 0:
            print("  💡 Há amostras de outros turnos hoje")
            print("  💡 Considere mostrar amostras de todos os turnos de hoje")
        else:
            print("  💡 Não há amostras hoje")
            if other_dates.count() > 0:
                print("  💡 Há amostras de outras datas")
                print("  💡 Considere mostrar amostras recentes")
    else:
        print("  ✅ Há amostras do turno atual")
    
    print("\n✅ Debug concluído!")

if __name__ == '__main__':
    debug_shift_data_detailed()
