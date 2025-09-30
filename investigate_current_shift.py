#!/usr/bin/env python
"""
Script para investigar dados do turno atual
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.utils import timezone
from quality_control.models import SpotSample, SpotAnalysis, Product, Property
from core.models import Shift, Plant, ProductionLine
import pytz

def investigate_current_shift():
    """Investigar dados do turno atual"""
    print("🔍 === INVESTIGAÇÃO TURNO ATUAL ===")
    
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
    
    # 1. Verificar todas as amostras
    print("\n1️⃣ TODAS as amostras no sistema:")
    all_samples = SpotSample.objects.all()
    print(f"  Total: {all_samples.count()}")
    
    for sample in all_samples:
        print(f"    - {sample.date} - Turno: {sample.shift.name} - {sample.product.name} - {sample.production_line.name}")
    
    # 2. Verificar amostras de hoje
    print("\n2️⃣ Amostras de hoje:")
    today_samples = SpotSample.objects.filter(date=today)
    print(f"  Total: {today_samples.count()}")
    
    for sample in today_samples:
        print(f"    - Turno: {sample.shift.name} - {sample.product.name} - {sample.production_line.name}")
    
    # 3. Verificar amostras do turno atual
    print(f"\n3️⃣ Amostras do turno atual ({current_shift.name}):")
    current_samples = SpotSample.objects.filter(date=today, shift=current_shift)
    print(f"  Total: {current_samples.count()}")
    
    if current_samples.exists():
        for sample in current_samples:
            print(f"    - {sample.product.name} - {sample.production_line.name} - Seq: {sample.sample_sequence}")
    else:
        print("    ❌ Nenhuma amostra do turno atual encontrada")
    
    # 4. Verificar turnos disponíveis
    print("\n4️⃣ Turnos disponíveis:")
    shifts = Shift.objects.all()
    for shift in shifts:
        print(f"  - {shift.name}: {shift.start_time} - {shift.end_time}")
    
    # 5. Verificar produtos e linhas
    print("\n5️⃣ Produtos e linhas disponíveis:")
    products = Product.objects.filter(is_active=True)
    lines = ProductionLine.objects.filter(is_active=True)
    print(f"  Produtos ativos: {products.count()}")
    print(f"  Linhas ativas: {lines.count()}")
    
    for line in lines:
        print(f"    - {line.name} ({line.plant.name})")
    
    # 6. Sugestão de solução
    print("\n6️⃣ Sugestão de solução:")
    if current_samples.count() == 0:
        print("  ❌ Não há amostras do turno atual")
        print("  💡 Precisamos criar dados de teste para o turno atual")
        
        # Verificar se há dados de outros turnos
        other_samples = SpotSample.objects.filter(date=today).exclude(shift=current_shift)
        if other_samples.exists():
            print(f"  💡 Há {other_samples.count()} amostras de outros turnos hoje")
            for sample in other_samples:
                print(f"    - Turno: {sample.shift.name} - {sample.product.name}")
        else:
            print("  💡 Não há amostras hoje em nenhum turno")
    else:
        print("  ✅ Há amostras do turno atual")
    
    print("\n✅ Investigação concluída!")

if __name__ == '__main__':
    investigate_current_shift()
