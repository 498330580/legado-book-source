from django.urls import path
from .views import (
    BookSearchView, BookDetailView, BookTocView, ChapterContentView,
    ExploreView, BookSourceView, BookSourcesView, HealthCheckView,
    ScrapingTaskView, RunScrapingTaskView,
    ScheduledTaskView, RunScheduledTaskView, CategoryListView
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('search/', BookSearchView.as_view(), name='book-search'),
    path('book/<str:book_id>/', BookDetailView.as_view(), name='book-detail'),
    path('book/<str:book_id>/toc/', BookTocView.as_view(), name='book-toc'),
    path('chapter/<str:chapter_id>/', ChapterContentView.as_view(), name='chapter-content'),
    path('explore/', ExploreView.as_view(), name='explore'),
    path('source/', BookSourceView.as_view(), name='book-source'),
    path('sources/', BookSourcesView.as_view(), name='book-sources'),
    path('scraping-tasks/', ScrapingTaskView.as_view(), name='scraping-tasks'),
    path('scraping-tasks/<int:task_id>/run/', RunScrapingTaskView.as_view(), name='run-scraping-task'),
    path('scheduled-tasks/', ScheduledTaskView.as_view(), name='scheduled-tasks'),
    path('scheduled-tasks/<int:task_id>/run/', RunScheduledTaskView.as_view(), name='run-scheduled-task'),
    path('scheduled-tasks/<int:task_id>/', RunScheduledTaskView.as_view(), name='delete-scheduled-task'),
    path('categories/', CategoryListView.as_view(), name='categories'),
]
