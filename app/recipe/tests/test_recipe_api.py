import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from django.test import TestCase

from rest_framework.test import APIClient

from core.models import Ingredient, Recipe, Tag

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse("recipe:recipe-list")

def image_upload_url(recipe_id):
	return reverse('recipe:recipe-upload-image', args=[recipe_id])

def detail_url(recipe_id):
	return reverse("recipe:recipe-detail", args=[recipe_id])

def sample_tag(user, name='Main Course'):
	return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name="Cinnamon"):
	return Ingredient.objects.create(user=user, name=name)


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

	def test_view_recipe_detail(self):
		tag = sample_tag(user=self.user)
		ingredient = sample_ingredient(user=self.user)

		recipe = sample_recipe(user=self.user)
		recipe.tags.add(tag)
		recipe.ingredients.add(ingredient)

		url = detail_url(recipe.id)

		res = self.client.get(url)

		serializer = RecipeDetailSerializer(recipe)

		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data, serializer.data)

	def test_create_basic_recipe(self):
		payload = {
			'title': 'Test Title',
			'time_minutes': 5,
			'price': 2.00
		}

		res = self.client.post(RECIPES_URL, payload)
		recipe = Recipe.objects.get(id=res.data['id'])

		self.assertEqual(res.status_code, status.HTTP_201_CREATED)

		for key in payload.keys():
			self.assertEqual(payload[key], getattr(recipe, key))

	def test_create_recipe_with_tags(self):
		tag1 = sample_tag(user=self.user, name='Pasta')
		tag2 = sample_tag(user=self.user, name='Italian')
		tag3 = sample_tag(user=self.user, name='Japan')

		payload = {
			'title': 'Meaty Spaghetti',
			'time_minutes': 5,
			'price': 2.00,
			'tags': [tag1.id, tag2.id]
		}

		res = self.client.post(RECIPES_URL, payload)
		recipe = Recipe.objects.get(id=res.data['id'])
		tags = recipe.tags.all()

		self.assertEqual(res.status_code, status.HTTP_201_CREATED)

		self.assertEqual(tags.count(), 2)

		self.assertIn(tag1, tags)
		self.assertIn(tag2, tags)
		self.assertNotIn(tag3, tags)


	def test_create_recipe_with_ingredients(self):
		ingredient1 = sample_ingredient(user=self.user, name='Shrimp')
		ingredient2 = sample_ingredient(user=self.user, name='Pepper')

		payload = {
			'title': 'Garlic Shrimp',
			'time_minutes': 5,
			'price': 2.00,
			'ingredients': [ingredient1.id, ingredient2.id]
		}

		res = self.client.post(RECIPES_URL, payload)

		recipe = Recipe.objects.get(id=res.data['id'])
		ingredients = recipe.ingredients.all()

		self.assertEqual(res.status_code, status.HTTP_201_CREATED)

		self.assertEqual(ingredients.count(), 2)
		self.assertIn(ingredient1, ingredients)
		self.assertIn(ingredient2, ingredients)


	def test_partial_update_recipe(self):
		recipe = sample_recipe(user=self.user)
		recipe.tags.add(sample_tag(user=self.user))

		new_tag = sample_tag(user=self.user, name='Bake')

		payload = {
				'title': 'Baked Mac',
				'tags': [new_tag.id]
		}

		url = detail_url(recipe.id)

		res = self.client.patch(url, payload)

		recipe.refresh_from_db()

		self.assertEqual(recipe.title, payload['title'])

		tags = recipe.tags.all()

		self.assertEqual(len(tags), 1)
		self.assertIn(new_tag, tags)

	def test_full_update_recipe(self):
		recipe = sample_recipe(user=self.user)
		recipe.tags.add(sample_tag(user=self.user))
		recipe.ingredients.add(sample_ingredient(user=self.user))

		#new_ingredient = sample_ingredient(user=self.user, name='Cesarian')

		payload = {
					'title': 'Caesarian Salad',
					'time_minutes': 10,
					'price': 20.00,
					#'ingredients': [new_ingredient.id]
				}

		url = detail_url(recipe.id)

		self.client.put(url, payload)
		recipe.refresh_from_db()
		tags = recipe.tags.all()
		ingredients = recipe.ingredients.all()

		for key in payload.keys():
			self.assertEqual(payload[key], getattr(recipe, key))

		self.assertEqual(len(tags), 0)
		self.assertEqual(len(ingredients), 0)
		#self.assertIn(new_ingredient.id, ingredients)

	def test_filter_recipes_by_tags(self):
		recipe1 = sample_recipe(user=self.user, title='Spaghetti Bolognese')
		recipe2 = sample_recipe(user=self.user, title='Tempura')

		tag1 = sample_tag(user=self.user, name='Pasta')
		tag2 = sample_tag(user=self.user, name='Seafood')

		recipe1.tags.add(tag1)
		recipe2.tags.add(tag2)

		recipe3 = sample_recipe(user=self.user, title='Tinola')
		tag3 = sample_tag(user=self.user, name='Filipino')
		recipe3.tags.add(tag3)

		res = self.client.get(
					RECIPES_URL,
					{'tags':f'{tag1.id},{tag2.id}'}
			)

		serializer1 = RecipeSerializer(recipe1)
		serializer2 = RecipeSerializer(recipe2)
		serializer3 = RecipeSerializer(recipe3)

		self.assertIn(serializer1.data, res.data)
		self.assertIn(serializer2.data, res.data)
		self.assertNotIn(serializer3.data, res.data)

	def test_filter_recipes_by_ingredients(self):
		recipe1 = sample_recipe(user=self.user, title='Spaghetti Bolognese')
		recipe2 = sample_recipe(user=self.user, title='Tuna Carbonara')

		ingredient1 = sample_tag(user=self.user, name='Ketchup')
		ingredient2 = sample_tag(user=self.user, name='Tuna')

		recipe1.tags.add(ingredient1)
		recipe2.tags.add(ingredient2)

		recipe3 = sample_recipe(user=self.user, title='Tinola')
		ingredient3 = sample_tag(user=self.user, name='Chicken')
		recipe3.tags.add(ingredient3)

		res = self.client.get(
					RECIPES_URL, 
					{'ingredients':f'{ingredient1.id},{ingredient2.id}'}
			)

		serializer1 = RecipeSerializer(recipe1)
		serializer2 = RecipeSerializer(recipe2)
		serializer3 = RecipeSerializer(recipe3)
		
		self.assertIn(serializer1.data, res.data)
		self.assertIn(serializer2.data, res.data)
		self.assertNotIn(serializer3.data, res.data)

		self.assertEqual(len(res), 2)


class RecipeImageUpload(TestCase):

	def setUp(self):
		self.client = APIClient()

		self.user = get_user_model().objects.create_user(
				'test@test.com',
				'password1234'
			)

		self.client.force_authenticate(self.user)

		self.recipe = sample_recipe(user=self.user)

	def tearDown(self):
		self.recipe.image.delete()

	def test_upload_image_to_recipe(self):
		url = image_upload_url(self.recipe.id)

		with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
			img = Image.new('RGB', (10, 10))
			img.save(ntf, format='JPEG')
			ntf.seek(0)
			res = self.client.post(url, {'image': ntf}, format='multipart')

		self.recipe.refresh_from_db()
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertIn('image', res.data)
		self.assertTrue(os.path.exists(self.recipe.image.path))

	def test_upload_image_bad_request(self):
		url = image_upload_url(self.recipe.id)

		res = self.client.post(url, {'image': 'notimage'}, format='multipart')

		self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
