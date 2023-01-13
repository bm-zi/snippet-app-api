"""
URL maping for snippet app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from snippet import views


router = DefaultRouter()
router.register('snippets', views.SnippetViewSet)
router.register('tags', views.TagViewSet)
router.register('source_codes', views.SourceCodeViewSet)

app_name = 'snippet'

urlpatterns = [
    path('', include(router.urls)),
]
