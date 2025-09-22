"""
Arquivo principal para deploy - Sistema de Controle de Qualidade Vermiculita
"""

import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

# Importar aplicação WSGI
application = get_wsgi_application()

if __name__ == "__main__":
    # Para desenvolvimento local
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
