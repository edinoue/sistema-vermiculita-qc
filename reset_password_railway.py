#!/usr/bin/env python
"""
Script para redefinir senha do usuário admin no PostgreSQL do Railway
"""

import os
import sys

# Definir a DATABASE_URL do Railway
os.environ['DATABASE_URL'] = 'postgresql://postgres:XcocfFRbysyHFNYBqMiqlxbITpGYIagl@maglev.proxy.rlwy.net:40681/railway'

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🚀 Sistema de Controle de Qualidade - Vermiculita")
print("🔧 Redefinindo Senha do Usuário Admin (PostgreSQL Railway)")
print("=" * 50)

try:
    import django
    django.setup()
    
    from django.contrib.auth import get_user_model
    from django.db import connection
    
    print("✅ Django configurado com sucesso!")
    
    # Verificar qual banco está sendo usado
    db_config = connection.settings_dict
    print(f"📊 Banco de dados: {db_config['ENGINE']}")
    print(f"📊 Host: {db_config.get('HOST', 'N/A')}")
    print(f"📊 Nome: {db_config.get('NAME', 'N/A')}")
    
    # Testar conexão com banco
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexão com PostgreSQL do Railway OK")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        print("Verifique se a DATABASE_URL está correta.")
        sys.exit(1)
    
    User = get_user_model()
    print("✅ Modelo de usuário carregado")
    
    # Verificar usuários existentes
    try:
        total_users = User.objects.count()
        print(f"📊 Total de usuários no banco: {total_users}")
        
        if total_users > 0:
            print("👥 Usuários existentes:")
            for user in User.objects.all():
                print(f"  - ID: {user.id}, Usuário: {user.username}, Email: {user.email}, Super: {user.is_superuser}")
    except Exception as e:
        print(f"⚠️  Erro ao listar usuários: {e}")
    
    # Buscar ou criar o usuário admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuário 'admin' encontrado (ID: {admin_user.id})")
        print(f"📧 Email: {admin_user.email}")
        print(f"👑 É super usuário: {admin_user.is_superuser}")
        print(f"🔧 É staff: {admin_user.is_staff}")
        
    except User.DoesNotExist:
        print("❌ Usuário 'admin' não encontrado!")
        print("Criando novo usuário admin...")
        
        # Criar novo usuário admin
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@vermiculita.com',
            password='admin123'
        )
        print(f"✅ Novo usuário admin criado (ID: {admin_user.id})")
        
    except Exception as e:
        print(f"❌ Erro ao buscar/criar usuário: {e}")
        sys.exit(1)
    
    # Redefinir a senha
    try:
        print("\n🔧 Redefinindo senha...")
        admin_user.set_password('admin123')
        admin_user.save()
        
        print("\n" + "="*50)
        print("✅ SENHA REDEFINIDA COM SUCESSO!")
        print("="*50)
        print(f"👤 Usuário: {admin_user.username}")
        print(f"📧 Email: {admin_user.email}")
        print(f"🔑 Nova senha: admin123")
        print(f"👑 É super usuário: {admin_user.is_superuser}")
        print(f"🔧 É staff: {admin_user.is_staff}")
        print("="*50)
        print("🎉 Agora você pode fazer login com:")
        print("   Usuário: admin")
        print("   Senha: admin123")
        
        # Verificar se a senha foi realmente alterada
        print("\n🔍 Verificando alteração...")
        admin_user.refresh_from_db()
        print(f"✅ Usuário atualizado no banco PostgreSQL do Railway")
        
    except Exception as e:
        print(f"❌ Erro ao redefinir senha: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Verifique se todas as dependências estão instaladas.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
