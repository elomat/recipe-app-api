
from rest_framework import status
from django.test import TestCase

from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


class PublicTest