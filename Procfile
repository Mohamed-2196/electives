web: gunicorn elective_system.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate && python manage.py load_courses courses_data.json
