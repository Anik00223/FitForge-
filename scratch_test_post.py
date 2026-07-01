import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
import django
from django.conf import settings
django.setup()
settings.DATABASES['default']['NAME'] = 'test_db.sqlite3'
settings.SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
settings.ALLOWED_HOSTS = ['*']

from django.core.management import call_command
call_command('migrate', verbosity=0)

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()
# Clean existing and create test user
User.objects.filter(email="test@example.com").delete()
user = User.objects.create_user(username="test@example.com", email="test@example.com", password="password123")

c = Client()
try:
    resp = c.post(reverse("login"), {"email": "test@example.com", "password": "password123"})
    print("STATUS CODE:", resp.status_code)
    print("LOCATION:", resp.get("Location", None))
    if resp.status_code == 500:
        resp.render()
        print(resp.content.decode())
except Exception as e:
    import traceback
    traceback.print_exc()
