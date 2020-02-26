from django.test import TestCase
from django.contrib.auth import get_user_model


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
