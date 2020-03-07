from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe.views import TagsViewSet, IngredientsViewSet

router = DefaultRouter()

router.register('tags', TagsViewSet)

router.register('ingredients', IngredientsViewSet)

app_name = 'recipe'

urlpatterns = [
	path('', include(router.urls))
]
