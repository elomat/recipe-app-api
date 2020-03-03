from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import TestCase

from rest_framework import status

from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')