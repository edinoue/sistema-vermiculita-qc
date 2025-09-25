#!/usr/bin/env python
"""
Script direto para criar super usuário sem depender de todas as configurações
"""

import os
import sys
import django
from django.conf import settings
from django.contrib.auth import get_user_model

# Configurações mínimas do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

# Configurações básicas para funcionar
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
        SECRET_KEY='temporary-key-for-superuser-creation',
        USE_TZ=True,
    )

django.setup()

def create_superuser():
    """Cria um super usuário"""
    
    print("🚀 Sistema de Controle de Qualidade - Vermiculita")
    print("🔧 Criação de Super Usuário")
    print("=" * 50)
    
    User = get_user_model()
    
    # Verificar se já existe um super usuário
    if User.objects.filter(is_superuser=True).exists():
        print("⚠️  Já existe um super usuário no sistema!")
        existing_superusers = User.objects.filter(is_superuser=True)
        print("Super usuários existentes:")
        for user in existing_superusers:
            print(f"  - {user.username} ({user.email})")
        
        response = input("\nDeseja criar um novo super usuário mesmo assim? (s/n): ")
        if response.lower() != 's':
            print("Operação cancelada.")
            return
    
    print("🔧 Criando super usuário...")
    print("=" * 50)
    
    # Coletar informações do super usuário
    username = input("Digite o nome de usuário: ").strip()
    if not username:
        print("❌ Nome de usuário é obrigatório!")
        return
    
    # Verificar se o usuário já existe
    if User.objects.filter(username=username).exists():
        print(f"❌ O usuário '{username}' já existe!")
        return
    
    email = input("Digite o email: ").strip()
    if not email:
        print("❌ Email é obrigatório!")
        return
    
    # Verificar se o email já existe
    if User.objects.filter(email=email).exists():
        print(f"❌ O email '{email}' já está em uso!")
        return
    
    password = input("Digite a senha: ").strip()
    if not password:
        print("❌ Senha é obrigatória!")
        return
    
    confirm_password = input("Confirme a senha: ").strip()
    if password != confirm_password:
        print("❌ As senhas não coincidem!")
        return
    
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
        
    except Exception as e:
        print(f"❌ Erro ao criar super usuário: {e}")
        return

def main():
    """Função principal"""
    try:
        create_superuser()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("Verifique se o banco de dados está configurado corretamente.")

if __name__ == "__main__":
    main()
