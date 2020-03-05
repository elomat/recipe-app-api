from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe.views import RetrieveListTags

router = DefaultRouter()

router.register('tags', RetrieveListTags)

app_name = 'recipe'

urlpatterns = [
	path('', include(router.urls)),
]