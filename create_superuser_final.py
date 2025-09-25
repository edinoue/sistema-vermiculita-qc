#!/usr/bin/env python
"""
Script final para criar super usuário - Sistema Vermiculita QC
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django com configurações mínimas
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

# Configurações básicas se não estiver configurado
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db.sqlite3',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
        ],
        SECRET_KEY='temporary-key-for-superuser-creation-12345',
        USE_TZ=True,
        AUTH_USER_MODEL='auth.User',
    )

try:
    django.setup()
    from django.contrib.auth import get_user_model
    from django.db import connection
    
    print("🚀 Sistema de Controle de Qualidade - Vermiculita")
    print("🔧 Criação de Super Usuário")
    print("=" * 50)
    
    # Verificar conexão com banco
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexão com banco de dados estabelecida")
    except Exception as e:
        print(f"❌ Erro de conexão com banco: {e}")
        print("Tentando criar banco de dados...")
        
        # Executar migrações básicas
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
    
    User = get_user_model()
    
    # Verificar se já existe um super usuário
    try:
        existing_superusers = User.objects.filter(is_superuser=True)
        if existing_superusers.exists():
            print("⚠️  Já existe super usuário(s) no sistema!")
            print("Super usuários existentes:")
            for user in existing_superusers:
                print(f"  - {user.username} ({user.email})")
            
            response = input("\nDeseja criar um novo super usuário mesmo assim? (s/n): ")
            if response.lower() != 's':
                print("Operação cancelada.")
                sys.exit(0)
    except Exception as e:
        print(f"⚠️  Aviso ao verificar usuários existentes: {e}")
    
    print("\n🔧 Criando super usuário...")
    print("=" * 30)
    
    # Coletar informações do super usuário
    username = input("Digite o nome de usuário: ").strip()
    if not username:
        print("❌ Nome de usuário é obrigatório!")
        sys.exit(1)
    
    # Verificar se o usuário já existe
    try:
        if User.objects.filter(username=username).exists():
            print(f"❌ O usuário '{username}' já existe!")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  Aviso ao verificar usuário existente: {e}")
    
    email = input("Digite o email: ").strip()
    if not email:
        print("❌ Email é obrigatório!")
        sys.exit(1)
    
    # Verificar se o email já existe
    try:
        if User.objects.filter(email=email).exists():
            print(f"❌ O email '{email}' já está em uso!")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  Aviso ao verificar email existente: {e}")
    
    password = input("Digite a senha: ").strip()
    if not password:
        print("❌ Senha é obrigatória!")
        sys.exit(1)
    
    confirm_password = input("Confirme a senha: ").strip()
    if password != confirm_password:
        print("❌ As senhas não coincidem!")
        sys.exit(1)
    
    try:
        # Criar o super usuário
        superuser = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        print("\n✅ Super usuário criado com sucesso!")
        print(f"👤 Usuário: {superuser.username}")
        print(f"📧 Email: {superuser.email}")
        print(f"🔑 ID: {superuser.id}")
        print(f"📅 Criado em: {superuser.date_joined}")
        
        print("\n🎉 Agora você pode fazer login no sistema!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erro ao criar super usuário: {e}")
        print("Detalhes do erro:")
        import traceback
        traceback.print_exc()
        sys.exit(1)

except Exception as e:
    print(f"❌ Erro ao configurar Django: {e}")
    print("Verifique se todas as dependências estão instaladas.")
    import traceback
    traceback.print_exc()
    sys.exit(1)
