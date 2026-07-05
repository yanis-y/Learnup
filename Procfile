release: python manage.py migrate --no-input && python manage.py collectstatic --no-input
web: gunicorn flashcards.wsgi --log-file - --bind 0.0.0.0:$PORT
