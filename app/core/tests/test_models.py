from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models
from core.models import Tag
from core.models import Ingredient
from core.models import Recipe

def sample_user(email='test@test.com', password='password1234'):
	return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

	def test_create_user_with_email_successful(self):
		"""test create user"""
		email = 'test@test.com'
		password = 'password1234'
		user = get_user_model().objects.create_user(
				email=email,
				password=password
			)

		self.assertEqual(user.email, email)
		self.assertTrue(user.check_password(password))

	def test_new_user_email_normalizer(self):
		"""test"""
		email = 'test@TEST.COM'
		user = get_user_model().objects.create_user(email, 'password1234')

		self.assertEqual(user.email, email.lower())

	def test_new_user_invalid_email(self):
		with self.assertRaises(ValueError):
			get_user_model().objects.create_user(None, 'password1234')

	def test_create_new_superuser(self):
		user = get_user_model().objects.create_superuser(
				'test@test.com',
				'password1234'
			)

		self.assertTrue(user.is_superuser)
		self.assertTrue(user.is_staff)

	def test_tag_str(self):
		tag = Tag.objects.create(
			user=sample_user(),
			name='Vegan'
			)

		self.assertEqual(str(tag), tag.name)

	def test_ingredients_str(self):
		ingredient = Ingredient.objects.create(
				user= sample_user(),
				name= 'Cucumber'
			)

		self.assertEqual(str(ingredient), ingredient.name)

	def test_recipe_srt(self):
		recipe = Recipe.objects.create(
				user=sample_user(),
				title='Title',
				time_minutes=5,
				price=5.00
			)

		self.assertEqual(str(recipe), recipe.title)


	@patch('uuid.uuid4')
	def test_recipe_file_name_uuid(self, mock_uuid):
		uuid = 'test-uuid'
		mock_uuid.return_value = uuid
		file_path = models.recipe_image_file_path(None, 'myimage.jpg')

		exp_path = f'uploads/recipe/{uuid}.jpg'

		self.assertEqual(file_path, exp_path)
		

