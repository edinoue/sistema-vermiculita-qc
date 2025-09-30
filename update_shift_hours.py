#!/usr/bin/env python
"""
Script para atualizar horários dos turnos no banco de dados
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from core.models import Shift

def update_shift_hours():
    """Atualizar horários dos turnos"""
    print("🔧 Atualizando horários dos turnos...")
    
    # Atualizar turno A: 7h-19h
    shift_a = Shift.objects.filter(name='A').first()
    if shift_a:
        shift_a.start_time = '07:00'
        shift_a.end_time = '19:00'
        shift_a.save()
        print(f"✅ Turno A atualizado: {shift_a.start_time} - {shift_a.end_time}")
    else:
        # Criar turno A se não existir
        shift_a = Shift.objects.create(
            name='A',
            start_time='07:00',
            end_time='19:00'
        )
        print(f"✅ Turno A criado: {shift_a.start_time} - {shift_a.end_time}")
    
    # Atualizar turno B: 19h-7h
    shift_b = Shift.objects.filter(name='B').first()
    if shift_b:
        shift_b.start_time = '19:00'
        shift_b.end_time = '07:00'
        shift_b.save()
        print(f"✅ Turno B atualizado: {shift_b.start_time} - {shift_b.end_time}")
    else:
        # Criar turno B se não existir
        shift_b = Shift.objects.create(
            name='B',
            start_time='19:00',
            end_time='07:00'
        )
        print(f"✅ Turno B criado: {shift_b.start_time} - {shift_b.end_time}")
    
    # Verificar turnos atualizados
    print("\n📋 Turnos no banco de dados:")
    shifts = Shift.objects.all()
    for shift in shifts:
        print(f"  - {shift.name}: {shift.start_time} - {shift.end_time}")
    
    print("\n✅ Atualização concluída!")

if __name__ == '__main__':
    update_shift_hours()
