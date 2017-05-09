"""
gunicorn WSGI server configuration.

to run:
gunicorn -b localhost:8000 metax_api.wsgi:application

"""
from multiprocessing import cpu_count
from os import environ

def max_workers():
    return cpu_count() * 2 + 1

bind = '0.0.0.0:8000'
max_requests = 1000
worker_class = 'gevent'
workers = max_workers()

secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
