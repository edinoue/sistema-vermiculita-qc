#!/usr/bin/env python
"""
Script para redefinir a senha do usuário admin
"""

import os
import sys

# Configurar variáveis de ambiente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')

print("🚀 Sistema de Controle de Qualidade - Vermiculita")
print("🔧 Redefinindo Senha do Usuário Admin")
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
        sys.exit(1)
    
    User = get_user_model()
    print("✅ Modelo de usuário carregado")
    
    # Buscar o usuário admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuário 'admin' encontrado (ID: {admin_user.id})")
        print(f"📧 Email atual: {admin_user.email}")
        print(f"👑 É super usuário: {admin_user.is_superuser}")
        print(f"🔧 É staff: {admin_user.is_staff}")
        
    except User.DoesNotExist:
        print("❌ Usuário 'admin' não encontrado!")
        print("Usuários disponíveis:")
        for user in User.objects.all():
            print(f"  - {user.username} ({user.email})")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao buscar usuário: {e}")
        sys.exit(1)
    
    # Redefinir a senha
    try:
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
        
    except Exception as e:
        print(f"❌ Erro ao redefinir senha: {e}")
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
