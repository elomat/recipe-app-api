from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):

	def setUp(self):
		self.client = APIClient()

	def test_user_not_login(self):
		res = self.client.get(INGREDIENTS_URL)

		self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):

	def setUp(self):
		self.user = get_user_model().objects.create_user(
				'test@test.com',
				'password1234'
			)

		self.client = APIClient()

		self.client.force_authenticate(self.user)

	def test_retrieve_ingredient_list(self):
		Ingredient.objects.create(name='Carrot',user=self.user)
		Ingredient.objects.create(name='Pork',user=self.user)

		res = self.client.get(INGREDIENTS_URL)

		ingredient = Ingredient.objects.all().order_by('-name')
		serializer = IngredientSerializer(ingredient, many=True)

		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data, serializer.data)

	def test_ingredients_limited_to_user(self):

		user2 = get_user_model().objects.create_user(
				'test2@test.com',
				'password1234'
			)
		
		Ingredient.objects.create(name='Sili',user=user2)
		Ingredient.objects.create(name='Carrot',user=user2)
		Ingredient.objects.create(name='Pork',user=user2)

		Ingredient.objects.create(name='Pepper',user=self.user)
		Ingredient.objects.create(name='Salt',user=self.user)

		ingredient = Ingredient.objects.filter(user=self.user).order_by('-name')
		serializer = IngredientSerializer(ingredient, many=True)

		res = self.client.get(INGREDIENTS_URL)

		self.assertEqual(len(res.data), 2)
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data, serializer.data)

	def test_create_ingredient(self):
		payload = {'name': 'Onion'}

		res = self.client.post(INGREDIENTS_URL, payload)
		
		is_exist = Ingredient.objects.filter(name='Onion').exists()

		self.assertTrue(is_exist)
		self.assertEqual(res.status_code, status.HTTP_201_CREATED)
