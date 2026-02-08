"""
WSGI config for novel_source_site project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_source_site.settings')

application = get_wsgi_application()
