#!/usr/bin/env python
"""
Script para configurar PostgreSQL corretamente no Railway
"""

def correct_railway_postgresql_setup():
    """Configurar PostgreSQL corretamente no Railway"""
    
    print("🚀 CONFIGURAÇÃO CORRETA DO POSTGRESQL NO RAILWAY")
    print("=" * 70)
    
    print("""
📋 PASSO A PASSO CORRETO:

1. ACESSAR RAILWAY DASHBOARD:
   - Acesse: https://railway.app/dashboard
   - Selecione seu projeto
   - Clique em 'New' → 'Database' → 'PostgreSQL'

2. AGUARDAR CRIAÇÃO COMPLETA:
   - Aguarde 2-3 minutos
   - Verifique se o status é 'Running'
   - Não use URLs internas

3. COPIAR DATABASE_URL CORRETA:
   - Clique no banco PostgreSQL
   - Vá na aba 'Connect'
   - Use a URL PÚBLICA (não interna)
   - Formato: postgresql://user:pass@host.railway.app:port/dbname

4. CONFIGURAR VARIÁVEL:
   - Vá em 'Variables'
   - Clique em 'New Variable'
   - Nome: DATABASE_URL
   - Valor: Cole a URL pública copiada
   - Clique em 'Add'

5. VERIFICAR CONFIGURAÇÃO:
   - A URL deve ter hostname público
   - Exemplo: host.railway.app (não postgres.railway.internal)
   - Porta deve ser 5432 ou similar

6. TESTAR CONEXÃO:
   - Execute: python check_database_config.py
   - Deve mostrar "PostgreSQL detectado"

✅ RESULTADO ESPERADO:
   - Sistema funcionando com PostgreSQL
   - Dados persistentes entre deploys
   - Backup automático no Railway
""")
    
    print("\n🔍 VERIFICAÇÕES IMPORTANTES:")
    print("✅ Hostname deve ser público (ex: host.railway.app)")
    print("❌ NÃO use postgres.railway.internal")
    print("✅ Porta deve ser 5432 ou similar")
    print("✅ URL deve começar com postgresql://")
    
    print("\n⚠️  PROBLEMAS COMUNS:")
    print("❌ Usar URL interna (postgres.railway.internal)")
    print("❌ Banco não estar completamente criado")
    print("❌ URL malformada ou incompleta")
    print("❌ Configurar antes do banco estar pronto")
    
    print("\n💡 DICAS:")
    print("• Aguarde o banco estar 'Running' antes de configurar")
    print("• Use sempre a URL pública do Railway")
    print("• Teste a conexão antes de fazer deploy")
    print("• Mantenha backup dos dados importantes")

if __name__ == '__main__':
    correct_railway_postgresql_setup()

