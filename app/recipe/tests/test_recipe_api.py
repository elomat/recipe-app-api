
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from django.test import TestCase

from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse("recipe:recipe-list")
print(RECIPES_URL)

def sample_recipe(user, **params):
	defaults = {
		'title': 'Test Title',
		'time_minutes': 5,
		'price': 2.00
	}

	defaults.update(params)

	return Recipe.objects.create(user=user, **defaults)


class PublicTestRecipeApi(TestCase):

	def setUp(self):
		self.client = APIClient()


	def test_auth_required(self):
		res = self.client.get(RECIPES_URL)

		self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTestRecipeApi(TestCase):

	def setUp(self):
		self.client = APIClient()

		self.user = get_user_model().objects.create_user(
				'test@test.com',
				'password1234'
			)

		self.client.force_authenticate(self.user)

	def test_retrieve_recipe(self):
		sample_recipe(user=self.user)
		
		res = self.client.get(RECIPES_URL)

		recipes = Recipe.objects.all().order_by("-id")
		serializer = RecipeSerializer(recipes, many=True)

		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data, serializer.data)

	def test_recipes_limited_to_user(self):
		user2 = get_user_model().objects.create_user(
				'test2@test.com',
				'password1234'
			)
		sample_recipe(user=user2)
		sample_recipe(user=self.user)
		sample_recipe(user=self.user)

		res = self.client.get(RECIPES_URL)

		recipes = Recipe.objects.filter(user=self.user).order_by("-id")
		serializer = RecipeSerializer(recipes, many=True)

		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data, serializer.data)
		self.assertEqual(len(res.data), 2)








