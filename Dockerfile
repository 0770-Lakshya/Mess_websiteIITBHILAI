FROM python:3.11.15-slim

WORKDIR /app



COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt



COPY . .



EXPOSE 8000



CMD ["bash", "-c", "cd /app && python manage.py migrate && (python manage.py createsuperuser --noinput || true) && python manage.py collectstatic --noinput && gunicorn mess_portal.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
