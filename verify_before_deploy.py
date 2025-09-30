#!/usr/bin/env python
"""
Script de verificação antes do deploy
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from quality_control.views import spot_dashboard_by_plant_view
from quality_control.models_production import ProductionRegistration
from core.models import Shift
from django.utils import timezone

def verify_before_deploy():
    """Verificar se tudo está funcionando antes do deploy"""
    print("🔍 === Verificação Pré-Deploy ===")
    
    errors = []
    warnings = []
    
    # 1. Verificar se as views estão funcionando
    print("\n1️⃣ Testando views...")
    try:
        factory = RequestFactory()
        request = factory.get('/qc/dashboard/spot/by-plant/')
        user = User.objects.first()
        if not user:
            user = User.objects.create_user('test', 'test@test.com', 'test123')
        request.user = user
        
        response = spot_dashboard_by_plant_view(request)
        if response.status_code == 200:
            print("  ✅ View spot_dashboard_by_plant_view funcionando")
        else:
            errors.append(f"View spot_dashboard_by_plant_view retornou status {response.status_code}")
            
    except Exception as e:
        errors.append(f"Erro na view spot_dashboard_by_plant_view: {str(e)}")
    
    # 2. Verificar se há turnos configurados
    print("\n2️⃣ Verificando turnos...")
    shifts = Shift.objects.all()
    if shifts.exists():
        print(f"  ✅ {shifts.count()} turnos encontrados")
        for shift in shifts:
            print(f"    - {shift.name}: {shift.start_time} - {shift.end_time}")
    else:
        warnings.append("Nenhum turno configurado")
    
    # 3. Verificar se há produção cadastrada
    print("\n3️⃣ Verificando produção...")
    today = timezone.now().date()
    current_shift = Shift.objects.filter(name='A').first() if 6 <= timezone.now().hour < 18 else Shift.objects.filter(name='B').first()
    
    if current_shift:
        production = ProductionRegistration.objects.filter(
            date=today,
            shift=current_shift,
            status='ACTIVE'
        ).first()
        
        if production:
            print(f"  ✅ Produção encontrada para {today} - Turno {current_shift.name}")
        else:
            warnings.append(f"Nenhuma produção ativa para {today} - Turno {current_shift.name}")
    else:
        warnings.append("Nenhum turno atual encontrado")
    
    # 4. Verificar arquivos de template
    print("\n4️⃣ Verificando templates...")
    template_path = 'templates/quality_control/spot_dashboard_by_plant.html'
    if os.path.exists(template_path):
        print(f"  ✅ Template {template_path} existe")
    else:
        errors.append(f"Template {template_path} não encontrado")
    
    # 5. Verificar URLs
    print("\n5️⃣ Verificando URLs...")
    try:
        from django.urls import reverse
        url = reverse('quality_control:spot_dashboard_by_plant')
        print(f"  ✅ URL spot_dashboard_by_plant: {url}")
    except Exception as e:
        errors.append(f"Erro na URL spot_dashboard_by_plant: {str(e)}")
    
    # 6. Verificar arquivos de deploy
    print("\n6️⃣ Verificando arquivos de deploy...")
    deploy_files = ['Procfile', 'railway.json', 'deploy_railway_final.py']
    for file in deploy_files:
        if os.path.exists(file):
            print(f"  ✅ {file} existe")
        else:
            errors.append(f"Arquivo {file} não encontrado")
    
    # 7. Verificar requirements.txt
    print("\n7️⃣ Verificando dependências...")
    if os.path.exists('requirements.txt'):
        print("  ✅ requirements.txt existe")
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
            print(f"    - {len(lines)} dependências listadas")
    else:
        errors.append("requirements.txt não encontrado")
    
    # Resumo
    print("\n" + "="*50)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("="*50)
    
    if errors:
        print(f"❌ ERROS ENCONTRADOS ({len(errors)}):")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    
    if warnings:
        print(f"⚠️  AVISOS ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    
    if not errors and not warnings:
        print("✅ TUDO OK! Pronto para deploy!")
        return True
    elif not errors:
        print("⚠️  Avisos encontrados, mas deploy pode prosseguir")
        return True
    else:
        print("❌ Erros encontrados! Corrigir antes do deploy")
        return False

if __name__ == '__main__':
    success = verify_before_deploy()
    sys.exit(0 if success else 1)
