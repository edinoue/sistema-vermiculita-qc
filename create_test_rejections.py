#!/usr/bin/env python
"""
Script para criar dados de teste com reprovações
"""

import os
import sys
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🧪 CRIANDO DADOS DE TESTE COM REPROVAÇÕES")
print("=" * 50)

try:
    import django
    django.setup()
    
    from quality_control.models import SpotAnalysis, CompositeSample, ProductionLine, Product, Property
    from django.contrib.auth.models import User
    from django.utils import timezone
    
    print("✅ Django configurado com sucesso!")
    
    # 1. Verificar se há dados existentes
    print("\n1. VERIFICANDO DADOS EXISTENTES:")
    
    spot_total = SpotAnalysis.objects.count()
    composite_total = CompositeSample.objects.count()
    
    print(f"   Análises pontuais: {spot_total}")
    print(f"   Amostras compostas: {composite_total}")
    
    # 2. Verificar se há linhas de produção e produtos
    lines = ProductionLine.objects.all()
    products = Product.objects.all()
    properties = Property.objects.all()
    
    print(f"   Linhas de produção: {lines.count()}")
    print(f"   Produtos: {products.count()}")
    print(f"   Propriedades: {properties.count()}")
    
    # 3. Se não há dados básicos, criar
    if lines.count() == 0:
        print("\n2. CRIANDO LINHA DE PRODUÇÃO:")
        line = ProductionLine.objects.create(
            name="Módulo I",
            code="M01",
            is_active=True
        )
        print(f"   ✅ Linha criada: {line.name}")
    else:
        line = lines.first()
        print(f"   ✅ Usando linha existente: {line.name}")
    
    if products.count() == 0:
        print("\n3. CRIANDO PRODUTO:")
        product = Product.objects.create(
            name="Vermiculita Concentrada Médio",
            code="CONC_MEDIO",
            is_active=True
        )
        print(f"   ✅ Produto criado: {product.name}")
    else:
        product = products.first()
        print(f"   ✅ Usando produto existente: {product.name}")
    
    if properties.count() == 0:
        print("\n4. CRIANDO PROPRIEDADES:")
        rendimento = Property.objects.create(
            name="RENDIMENTO",
            description="Rendimento na Expansão",
            unit="m³/t",
            is_active=True
        )
        teor = Property.objects.create(
            name="TEOR",
            description="Teor de Vermiculita",
            unit="%",
            is_active=True
        )
        print(f"   ✅ Propriedades criadas: {rendimento.name}, {teor.name}")
    else:
        rendimento = properties.filter(name="RENDIMENTO").first()
        teor = properties.filter(name="TEOR").first()
        print(f"   ✅ Usando propriedades existentes")
    
    # 4. Obter usuário admin
    print("\n4. OBTENDO USUÁRIO ADMIN:")
    try:
        admin_user = User.objects.get(username='admin')
        print(f"   ✅ Usuário admin encontrado: {admin_user.username}")
    except User.DoesNotExist:
        print("   ❌ Usuário admin não encontrado!")
        sys.exit(1)
    
    # 5. Criar análises pontuais com reprovações
    print("\n5. CRIANDO ANÁLISES PONTUAIS COM REPROVAÇÕES:")
    
    now = timezone.now()
    
    # Criar algumas análises aprovadas
    for i in range(3):
        analysis = SpotAnalysis.objects.create(
            production_line=line,
            product=product,
            property=rendimento if i % 2 == 0 else teor,
            value=9.0 if i % 2 == 0 else 90.0,
            sample_time=now - timedelta(hours=i),
            status='APPROVED',
            operator=admin_user
        )
        print(f"   ✅ Análise aprovada criada: {analysis.id}")
    
    # Criar algumas análises reprovadas
    for i in range(2):
        analysis = SpotAnalysis.objects.create(
            production_line=line,
            product=product,
            property=rendimento if i % 2 == 0 else teor,
            value=7.0 if i % 2 == 0 else 70.0,  # Valores baixos para reprovação
            sample_time=now - timedelta(hours=i+3),
            status='REJECTED',
            operator=admin_user
        )
        print(f"   ✅ Análise reprovada criada: {analysis.id}")
    
    # 5. Criar amostras compostas com reprovações
    print("\n6. CRIANDO AMOSTRAS COMPOSTAS COM REPROVAÇÕES:")
    
    # Amostra aprovada
    composite_approved = CompositeSample.objects.create(
        production_line=line,
        product=product,
        date=now.date(),
        shift="A",
        status='APPROVED',
        operator=admin_user
    )
    print(f"   ✅ Amostra composta aprovada criada: {composite_approved.id}")
    
    # Amostra reprovada
    composite_rejected = CompositeSample.objects.create(
        production_line=line,
        product=product,
        date=now.date(),
        shift="A",
        status='REJECTED',
        operator=admin_user
    )
    print(f"   ✅ Amostra composta reprovada criada: {composite_rejected.id}")
    
    # 6. Verificar totais finais
    print("\n7. VERIFICANDO TOTAIS FINAIS:")
    
    spot_rejected = SpotAnalysis.objects.filter(status='REJECTED').count()
    composite_rejected = CompositeSample.objects.filter(status='REJECTED').count()
    total_rejections = spot_rejected + composite_rejected
    
    print(f"   Reprovações pontuais: {spot_rejected}")
    print(f"   Reprovações compostas: {composite_rejected}")
    print(f"   Total reprovações: {total_rejections}")
    
    # 7. Resultado final
    print("\n" + "="*50)
    print("RESULTADO FINAL:")
    
    if total_rejections > 0:
        print(f"✅ Dados de teste criados com sucesso!")
        print(f"✅ O dashboard agora deveria mostrar {total_rejections} reprovações")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Acesse o sistema no navegador")
        print("2. Vá para o dashboard")
        print("3. Verifique se o número de reprovações está sendo exibido")
        print("4. Se ainda não funcionar, verifique o console do navegador para erros")
    else:
        print("❌ Não foi possível criar dados de teste")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
