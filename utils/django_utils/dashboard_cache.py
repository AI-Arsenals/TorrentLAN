import os
import sys
from django.core.cache import cache

# Specify the absolute path to your Django project directory
DJANGO_PROJECT_PATH = './django_for_frontend'

sys.path.append(DJANGO_PROJECT_PATH)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_for_frontend.settings')

import django
django.setup()

# def cache_fetch(only_fetch=False):
#     if only_fetch:
#         value = cache.get('Dashboard')
#         if value is None:
#             return False
#         return value
    
#     cache.lock('Dashboard').acquire()
#     value = cache.get('Dashboard')
#     if value is None:
#         return False
#     return value

# def cache_update(value):
#     cache.set('Dashboard', value)
#     cache.lock('Dashboard').release()


# Below is to enhance caching in later versions
# def cache_fetch_all():
#     res=cache_fetch_lazy_file_list()
#     if res is False:
#         return False
    
#     return_data=[]
#     for lazy_file in res:
#         return_data.append(cache_fetch(lazy_file))

# def cache_fetch_lazy_file_list():
#     value = cache.get('Dashboard_lazy_file_list')
#     if value is None:
#         return False
#     return value

# def cache_update_lazy_file_list(lazy_file_hash):
#     value = cache.get('Dashboard_lazy_file_list')
#     if value is None:
#         value=[]
#         value.append(lazy_file_hash)
#         cache.set('Dashboard_lazy_file_list', value)
#         return True
#     if lazy_file_hash not in value:
#         value.append(lazy_file_hash)
#         cache.set('Dashboard_lazy_file_list', value)
#         return True

# def cache_fetch(lazy_file):
#     value = cache.get(lazy_file)
#     if value is None:
#         return False
#     return value

# def cache_update_lazy_file(lazty_file_hash,value):
#     cache.set(lazty_file_hash, value)

#     # update list
#     cache_update_lazy_file_list(lazty_file_hash)      


if __name__ == '__main__':
    cache_update('test')
    print(cache_fetch())
