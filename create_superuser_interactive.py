#!/usr/bin/env python
"""
Script interativo para criar super usuário
"""

import os
import sys

# Configurar variáveis de ambiente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🚀 Sistema de Controle de Qualidade - Vermiculita")
print("🔧 Criação de Super Usuário")
print("=" * 50)

try:
    import django
    django.setup()
    
    from django.contrib.auth import get_user_model
    from django.db import connection
    
    print("✅ Django configurado com sucesso!")
    
    # Testar conexão com banco
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexão com banco de dados OK")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        print("Tentando executar migrações...")
        
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
    
    User = get_user_model()
    print("✅ Modelo de usuário carregado")
    
    # Verificar usuários existentes
    try:
        total_users = User.objects.count()
        superusers = User.objects.filter(is_superuser=True).count()
        print(f"📊 Total de usuários: {total_users}")
        print(f"👑 Super usuários: {superusers}")
        
        if superusers > 0:
            print("\n⚠️  Super usuários existentes:")
            for user in User.objects.filter(is_superuser=True):
                print(f"  - {user.username} ({user.email})")
    except Exception as e:
        print(f"⚠️  Erro ao verificar usuários: {e}")
    
    print("\n" + "="*50)
    print("🔧 CRIANDO NOVO SUPER USUÁRIO")
    print("="*50)
    
    # Coletar dados
    username = input("\nDigite o nome de usuário: ").strip()
    if not username:
        print("❌ Nome de usuário é obrigatório!")
        sys.exit(1)
    
    email = input("Digite o email: ").strip()
    if not email:
        print("❌ Email é obrigatório!")
        sys.exit(1)
    
    password = input("Digite a senha: ").strip()
    if not password:
        print("❌ Senha é obrigatória!")
        sys.exit(1)
    
    confirm_password = input("Confirme a senha: ").strip()
    if password != confirm_password:
        print("❌ As senhas não coincidem!")
        sys.exit(1)
    
    # Verificar se usuário já existe
    if User.objects.filter(username=username).exists():
        print(f"❌ O usuário '{username}' já existe!")
        sys.exit(1)
    
    if User.objects.filter(email=email).exists():
        print(f"❌ O email '{email}' já está em uso!")
        sys.exit(1)
    
    # Criar super usuário
    try:
        superuser = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        print("\n" + "="*50)
        print("✅ SUPER USUÁRIO CRIADO COM SUCESSO!")
        print("="*50)
        print(f"👤 Usuário: {superuser.username}")
        print(f"📧 Email: {superuser.email}")
        print(f"🔑 ID: {superuser.id}")
        print(f"📅 Criado em: {superuser.date_joined}")
        print(f"👑 É super usuário: {superuser.is_superuser}")
        print(f"🔧 É staff: {superuser.is_staff}")
        print("="*50)
        print("🎉 Agora você pode fazer login no sistema!")
        
    except Exception as e:
        print(f"❌ Erro ao criar super usuário: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Verifique se o Django está instalado corretamente.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
