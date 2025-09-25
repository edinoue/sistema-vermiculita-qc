#!/usr/bin/env python
"""
Script para redefinir senha usando SQLite diretamente
"""

import os
import sys
import sqlite3
from pathlib import Path

print("🚀 Sistema de Controle de Qualidade - Vermiculita")
print("🔧 Redefinindo Senha do Usuário Admin (SQLite)")
print("=" * 50)

# Verificar se o banco SQLite existe
db_path = Path("db.sqlite3")
if not db_path.exists():
    print("❌ Banco de dados SQLite não encontrado!")
    print("Arquivos na pasta atual:")
    for file in Path(".").glob("*.sqlite*"):
        print(f"  - {file}")
    sys.exit(1)

print(f"✅ Banco SQLite encontrado: {db_path}")

try:
    # Conectar ao banco SQLite
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    
    # Verificar se a tabela auth_user existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'")
    if not cursor.fetchone():
        print("❌ Tabela auth_user não encontrada!")
        conn.close()
        sys.exit(1)
    
    print("✅ Tabela auth_user encontrada")
    
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
        conn.close()
        sys.exit(1)
    
    print(f"✅ Usuário admin encontrado (ID: {admin_user[0]})")
    
    # Importar Django para usar o sistema de hash de senha
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
    
    import django
    django.setup()
    
    from django.contrib.auth.hashers import make_password
    
    # Gerar hash da nova senha
    new_password_hash = make_password('admin123')
    print(f"🔑 Hash da nova senha gerado")
    
    # Atualizar a senha no banco
    cursor.execute(
        "UPDATE auth_user SET password = ? WHERE username = 'admin'",
        (new_password_hash,)
    )
    
    # Confirmar a alteração
    conn.commit()
    
    # Verificar se a alteração foi feita
    cursor.execute("SELECT username, email FROM auth_user WHERE username = 'admin'")
    updated_user = cursor.fetchone()
    
    print("\n" + "="*50)
    print("✅ SENHA REDEFINIDA COM SUCESSO!")
    print("="*50)
    print(f"👤 Usuário: {updated_user[0]}")
    print(f"📧 Email: {updated_user[1]}")
    print(f"🔑 Nova senha: admin123")
    print("="*50)
    print("🎉 Agora você pode fazer login com:")
    print("   Usuário: admin")
    print("   Senha: admin123")
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"❌ Erro do SQLite: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
