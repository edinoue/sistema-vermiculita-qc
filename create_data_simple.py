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

# Obter turno atual
brazil_tz = pytz.timezone('America/Sao_Paulo')
current_time_brazil = timezone.now().astimezone(brazil_tz)
today = timezone.now().date()

if 7 <= current_time_brazil.hour < 19:
    current_shift = Shift.objects.filter(name='A').first()
else:
    current_shift = Shift.objects.filter(name='B').first()

print(f"Turno atual: {current_shift.name if current_shift else 'Nenhum'}")

# Verificar se já há dados
existing = SpotSample.objects.filter(date=today, shift=current_shift)
print(f"Amostras existentes: {existing.count()}")

if existing.count() == 0:
    print("Criando dados...")
    
    # Criar planta e linha
    plant, _ = Plant.objects.get_or_create(name="Módulo I", defaults={'is_active': True})
    line, _ = ProductionLine.objects.get_or_create(name="Filial 04", plant=plant, defaults={'is_active': True})
    
    # Criar produtos
    products = []
    for i in range(1, 5):
        product, _ = Product.objects.get_or_create(name=f"Vermiculita {i}", defaults={'is_active': True})
        products.append(product)
    
    # Criar propriedades
    prop1, _ = Property.objects.get_or_create(name="Teor de Vermiculita", defaults={'unit': '%', 'display_order': 1, 'is_active': True})
    prop2, _ = Property.objects.get_or_create(name="Rendimento na Expansão", defaults={'unit': 'kg/m³', 'display_order': 2, 'is_active': True})
    
    # Criar amostras
    for i, product in enumerate(products):
        sample = SpotSample.objects.create(
            product=product,
            production_line=line,
            shift=current_shift,
            date=today,
            sample_sequence=i + 1,
            observations=f"Amostra {i + 1}",
            sample_time=timezone.now().time()
        )
        
        # Criar análises
        SpotAnalysis.objects.create(
            spot_sample=sample,
            property=prop1,
            value=f"{85 + i * 2}",
            status="APPROVED"
        )
        
        SpotAnalysis.objects.create(
            spot_sample=sample,
            property=prop2,
            value=f"{1200 + i * 50}",
            status="APPROVED"
        )
        
        print(f"Criada amostra {i + 1}")

print("Concluído!")
