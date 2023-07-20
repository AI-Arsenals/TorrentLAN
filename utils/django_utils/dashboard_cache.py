import os
import sys
from django.core.cache import cache

# Specify the absolute path to your Django project directory
DJANGO_PROJECT_PATH = './django_for_frontend'

sys.path.append(DJANGO_PROJECT_PATH)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_for_frontend.settings')

import django
django.setup()

def cache_fetch():
    value = cache.get('Dashboard')
    if value is None:
        return False
    return value

def cache_update(value):
    cache.set('Dashboard', value)

if __name__ == '__main__':
    cache_update('test')
    print(cache_fetch())
