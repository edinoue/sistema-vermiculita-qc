"""
Aplicação principal para deploy - Sistema de Controle de Qualidade Vermiculita
"""

import os
import django
from django.core.wsgi import get_wsgi_application

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vermiculita_system.settings')
django.setup()

# Aplicação WSGI
app = get_wsgi_application()

# Para compatibilidade com diferentes plataformas
application = app

if __name__ == "__main__":
    # Executar servidor de desenvolvimento
    import sys
    from django.core.management import execute_from_command_line
    
    if len(sys.argv) == 1:
        sys.argv.append('runserver')
        sys.argv.append('0.0.0.0:8000')
    
    execute_from_command_line(sys.argv)
