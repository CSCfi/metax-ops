bind = "0.0.0.0:8000"
workers = 3
secure_scheme_headers = {
 'X-FORWARDED-PROTOCOL': 'ssl',
 'X-FORWARDED-PROTO': 'https',
 'X-FORWARDED-SSL': 'on'
 }
