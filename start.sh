#!/bin/bash

# Script de inicialização para produção

echo "🚀 Iniciando Sistema de Controle de Qualidade - Vermiculita"

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Executar migrações
echo "🗄️ Executando migrações do banco de dados..."
python manage.py migrate

# Criar superusuário se não existir
echo "👤 Verificando superusuário..."
python manage.py shell << EOF
from django.contrib.auth.models import User
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@vermiculita.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superusuário '{username}' criado com sucesso!")
else:
    print(f"Superusuário '{username}' já existe.")
EOF

# Popular dados iniciais se necessário
echo "📊 Verificando dados iniciais..."
python manage.py shell << EOF
from core.models import Plant, ProductionLine, Shift
from quality_control.models import Product, Property, Specification
from django.contrib.auth.models import User

# Verificar se já existem dados
if not Plant.objects.exists():
    print("Populando dados iniciais...")
    exec(open('populate_initial_data.py').read())
    print("Dados iniciais criados!")
else:
    print("Dados iniciais já existem.")
EOF

echo "✅ Sistema inicializado com sucesso!"

# Iniciar servidor
echo "🌐 Iniciando servidor web..."
exec gunicorn vermiculita_system.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120
