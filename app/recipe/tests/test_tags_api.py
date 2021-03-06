from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status

from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):

	def setUp(self):
		self.client = APIClient()


	def test_login_required(self):
		res = self.client.get(TAGS_URL)

		self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):

	def setUp(self):
		self.user = get_user_model().objects.create_user(
				'test@test.com',
				'password1234'
			)
		self.client = APIClient()
		self.client.force_authenticate(self.user)

	def test_retrieve_tags(self):
		Tag.objects.create(user=self.user, name='Vegan')
		Tag.objects.create(user=self.user, name='Dessert')

		tags = Tag.objects.all().order_by('-name')
		serializer = TagSerializer(tags, many=True)
		
		res = self.client.get(TAGS_URL)
		
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data, serializer.data)


	def test_tags_limited_to_user(self):
		user2 = get_user_model().objects.create_user(
				'test1@test.com',
				'password1234'
			)

		Tag.objects.create(user=self.user, name="Vegan")
		Tag.objects.create(user=self.user, name="Dessert")
		Tag.objects.create(user=user2, name="Menudo")

		tags = Tag.objects.filter(user=self.user).order_by("-name")
		serializer = TagSerializer(tags, many=True)
		
		res = self.client.get(TAGS_URL)
		
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data, serializer.data)

	def test_create_tags_success(self):
		payload = {'name': 'Vegan'}
		res = self.client.post(TAGS_URL, payload)

		is_exists = Tag.objects.filter(
				user=self.user, 
				name=payload['name']
			).exists()

		self.assertTrue(is_exists)

		self.assertEqual(res.status_code, status.HTTP_201_CREATED)


	def test_invalid_tag(self):
		payload = {'name': ''}

		res = self.client.post(TAGS_URL, payload)

		self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)