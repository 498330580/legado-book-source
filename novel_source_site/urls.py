"""
URL configuration for novel_source_site project.
"""
from django.contrib import admin
from django.urls import path, include
from books.views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('books.urls')),
]
