web: python manage.py collectstatic --noinput && python deploy_railway_final.py && gunicorn vermiculita_system.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate
