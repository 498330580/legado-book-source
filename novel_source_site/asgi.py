"""
ASGI config for novel_source_site project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_source_site.settings')

application = get_asgi_application()
