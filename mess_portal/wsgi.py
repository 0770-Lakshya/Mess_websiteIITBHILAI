"""WSGI config for mess_portal project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mess_portal.settings')

application = get_wsgi_application()