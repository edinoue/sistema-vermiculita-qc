#!/usr/bin/env python
"""
Guia completo para configurar PostgreSQL no Railway
"""

def railway_postgresql_setup():
    """Guia completo para configurar PostgreSQL no Railway"""
    
    print("🚀 CONFIGURAÇÃO COMPLETA DO POSTGRESQL NO RAILWAY")
    print("=" * 70)
    
    print("""
📋 PASSO A PASSO DETALHADO:

1. ACESSAR RAILWAY DASHBOARD:
   - Acesse: https://railway.app/dashboard
   - Faça login com sua conta
   - Selecione seu projeto

2. ADICIONAR BANCO POSTGRESQL:
   - Clique em "New" (botão azul)
   - Selecione "Database"
   - Escolha "PostgreSQL"
   - Aguarde a criação (2-3 minutos)

3. COPIAR DATABASE_URL:
   - Após criação, clique no banco PostgreSQL
   - Vá na aba "Connect"
   - Copie a "DATABASE_URL" completa
   - Exemplo: postgresql://user:pass@host:port/dbname

4. CONFIGURAR VARIÁVEL DE AMBIENTE:
   - No Railway, vá em "Variables"
   - Clique em "New Variable"
   - Nome: DATABASE_URL
   - Valor: Cole a URL copiada
   - Clique em "Add"

5. VERIFICAR CONFIGURAÇÃO:
   - Execute: python check_database_config.py
   - Deve mostrar "PostgreSQL detectado"

6. APLICAR MIGRAÇÕES:
   - Execute: python manage.py migrate
   - Ou aguarde deploy automático

7. CRIAR SUPERUSUÁRIO:
   - Execute: python manage.py createsuperuser
   - Ou use o console do Railway

✅ RESULTADO ESPERADO:
   - Dados persistentes entre deploys
   - Backup automático no Railway
   - Sistema escalável para produção
""")
    
    print("\n🔧 SCRIPTS DE APOIO:")
    print("   - check_database_config.py: Verificar configuração")
    print("   - setup_railway_database.py: Configuração automática")
    print("   - backup_system.py: Backup de dados")
    print("   - deploy_safe_with_persistence.py: Deploy seguro")
    
    print("\n⚠️  IMPORTANTE:")
    print("   - Faça backup dos dados atuais antes de mudar")
    print("   - Teste a configuração antes de usar em produção")
    print("   - Mantenha a DATABASE_URL segura")

if __name__ == '__main__':
    railway_postgresql_setup()




