"""
URL maping for snippet app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from snippet import views


router = DefaultRouter()
router.register('snippets', views.SnippetViewSet)

app_name = 'snippet'

urlpatterns = [
    path('', include(router.urls)),
]
