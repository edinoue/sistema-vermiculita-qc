#!/usr/bin/env python
"""
Script para debugar dados por turno
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

def debug_shift_data():
    """Debugar dados por turno"""
    print("🔍 === DEBUG SHIFT DATA ===")
    
    current_time = timezone.now()
    today = timezone.now().date()
    
    print(f"📅 Data atual: {today}")
    print(f"🕐 Hora atual: {current_time.hour}:{current_time.minute}")
    
    # 1. Verificar turnos disponíveis
    print("\n1️⃣ Turnos disponíveis:")
    shifts = Shift.objects.all()
    for shift in shifts:
        print(f"  - {shift.name}: {shift.start_time} - {shift.end_time}")
    
    # 2. Determinar turno atual
    current_shift = None
    if 6 <= current_time.hour < 18:
        current_shift = Shift.objects.filter(name='A').first()
        print(f"\n2️⃣ Turno atual detectado: A (6h-18h)")
    else:
        current_shift = Shift.objects.filter(name='B').first()
        print(f"\n2️⃣ Turno atual detectado: B (18h-6h)")
    
    if current_shift:
        print(f"  Turno encontrado: {current_shift.name}")
    else:
        print("  ❌ Nenhum turno encontrado!")
    
    # 3. Verificar amostras por turno
    print("\n3️⃣ Amostras por turno hoje:")
    for shift in shifts:
        samples = SpotSample.objects.filter(date=today, shift=shift)
        print(f"  Turno {shift.name}: {samples.count()} amostras")
        
        for sample in samples[:3]:  # Mostrar apenas 3
            print(f"    - {sample.product.name} - {sample.production_line.name} - Seq: {sample.sample_sequence}")
    
    # 4. Verificar amostras do turno atual
    if current_shift:
        print(f"\n4️⃣ Amostras do turno atual ({current_shift.name}):")
        current_samples = SpotSample.objects.filter(date=today, shift=current_shift)
        print(f"  Total: {current_samples.count()}")
        
        for sample in current_samples:
            print(f"    - {sample.product.name} - {sample.production_line.name} - Seq: {sample.sample_sequence}")
            analyses = SpotAnalysis.objects.filter(spot_sample=sample)
            print(f"      Análises: {analyses.count()}")
    else:
        print("\n4️⃣ Nenhum turno atual definido")
    
    # 5. Verificar amostras de outros turnos
    print("\n5️⃣ Amostras de outros turnos hoje:")
    other_samples = SpotSample.objects.filter(date=today).exclude(shift=current_shift) if current_shift else SpotSample.objects.filter(date=today)
    print(f"  Total: {other_samples.count()}")
    
    for sample in other_samples:
        print(f"    - Turno: {sample.shift.name} - {sample.product.name} - {sample.production_line.name}")
    
    # 6. Verificar se há dados de outras datas
    print("\n6️⃣ Amostras de outras datas:")
    other_dates = SpotSample.objects.exclude(date=today).order_by('-date')[:5]
    print(f"  Total: {other_dates.count()}")
    
    for sample in other_dates:
        print(f"    - {sample.date} - Turno: {sample.shift.name} - {sample.product.name}")
    
    # 7. Sugestão de solução
    print("\n7️⃣ Sugestão de solução:")
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
    debug_shift_data()
