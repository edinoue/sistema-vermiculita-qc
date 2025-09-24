web: python manage.py collectstatic --noinput && python deploy_safe.py && gunicorn vermiculita_system.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate
