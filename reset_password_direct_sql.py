#!/usr/bin/env python
"""
Script para redefinir senha usando SQL direto no PostgreSQL
"""

import os
import sys

print("🚀 Sistema de Controle de Qualidade - Vermiculita")
print("🔧 Redefinindo Senha do Usuário Admin (SQL Direto)")
print("=" * 50)

try:
    # Tentar instalar psycopg2 se não estiver disponível
    try:
        import psycopg2
        print("✅ psycopg2 disponível")
    except ImportError:
        print("⚠️  psycopg2 não encontrado, tentando instalar...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        import psycopg2
        print("✅ psycopg2 instalado com sucesso")
    
    # Conectar ao PostgreSQL
    conn = psycopg2.connect(
        host="maglev.proxy.rlwy.net",
        port="40681",
        database="railway",
        user="postgres",
        password="XcocfFRbysyHFNYBqMiqlxbITpGYIagl"
    )
    
    print("✅ Conectado ao PostgreSQL do Railway")
    
    cursor = conn.cursor()
    
    # Verificar se a tabela auth_user existe
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'auth_user'
    """)
    
    if not cursor.fetchone():
        print("❌ Tabela auth_user não encontrada!")
        print("Executando migrações...")
        
        # Executar migrações básicas
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
        os.environ['DATABASE_URL'] = 'postgresql://postgres:XcocfFRbysyHFNYBqMiqlxbITpGYIagl@maglev.proxy.rlwy.net:40681/railway'
        
        import django
        django.setup()
        
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
        
        print("✅ Migrações executadas")
    
    # Verificar usuários existentes
    cursor.execute("SELECT id, username, email, is_superuser, is_staff FROM auth_user")
    users = cursor.fetchall()
    
    print(f"📊 Total de usuários: {len(users)}")
    for user in users:
        print(f"  - ID: {user[0]}, Usuário: {user[1]}, Email: {user[2]}, Super: {user[3]}, Staff: {user[4]}")
    
    # Buscar o usuário admin
    cursor.execute("SELECT id, username, email FROM auth_user WHERE username = 'admin'")
    admin_user = cursor.fetchone()
    
    if not admin_user:
        print("❌ Usuário 'admin' não encontrado!")
        print("Criando novo usuário admin...")
        
        # Importar Django para usar o sistema de hash de senha
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
        os.environ['DATABASE_URL'] = 'postgresql://postgres:XcocfFRbysyHFNYBqMiqlxbITpGYIagl@maglev.proxy.rlwy.net:40681/railway'
        
        import django
        django.setup()
        
        from django.contrib.auth.hashers import make_password
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Criar novo usuário admin
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@vermiculita.com',
            password='admin123'
        )
        
        print(f"✅ Novo usuário admin criado (ID: {admin_user.id})")
    else:
        print(f"✅ Usuário admin encontrado (ID: {admin_user[0]})")
        
        # Importar Django para usar o sistema de hash de senha
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
        os.environ['DATABASE_URL'] = 'postgresql://postgres:XcocfFRbysyHFNYBqMiqlxbITpGYIagl@maglev.proxy.rlwy.net:40681/railway'
        
        import django
        django.setup()
        
        from django.contrib.auth.hashers import make_password
        
        # Gerar hash da nova senha
        new_password_hash = make_password('admin123')
        print(f"🔑 Hash da nova senha gerado")
        
        # Atualizar a senha no banco
        cursor.execute(
            "UPDATE auth_user SET password = %s WHERE username = 'admin'",
            (new_password_hash,)
        )
        
        # Confirmar a alteração
        conn.commit()
        
        print("\n" + "="*50)
        print("✅ SENHA REDEFINIDA COM SUCESSO!")
        print("="*50)
        print(f"👤 Usuário: {admin_user[1]}")
        print(f"📧 Email: {admin_user[2]}")
        print(f"🔑 Nova senha: admin123")
        print("="*50)
        print("🎉 Agora você pode fazer login com:")
        print("   Usuário: admin")
        print("   Senha: admin123")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
