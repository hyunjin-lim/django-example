# DjangoTest

from django.test import TestCase
from apps.users.models import User

# Create your tests here.

class UserTest(TestCase):
    """ Test module for Puppy model """

    def setUp(self):
        User.objects.create(
            email='test@abcd.com', password="1234", username="test1")
        User.objects.create(
            email='test2@abcd.com', password="1234", username="test2")

    def test_user_create(self):
        puppy_casper = User.objects.get(email='test@abcd.com')
        puppy_muffin = User.objects.get(email='test2@abcd.com')
        self.assertEqual(
            puppy_casper.username, "test1")
        self.assertEqual(
            puppy_muffin.username, "test3")

