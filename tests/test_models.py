from sys import exit  # Pure Python imports

from django.contrib.auth.hashers import make_password
from django.test import TestCase  # 3rd party libs

from event_organizer.models import Player  # our code


class TestPlayerModel(TestCase):

    def setUp(self):
        self.player = Player(
            first_name="Immanuel",
            last_name="Kant",
            email="email.email@false.com",
            _password=make_password("pass")
        )

    def test_check_password_correct_password(self):
        result = self.player.check_password("pass")

        self.assertTrue(result)

    def test_check_password_wrong_password(self):
        result = self.player.check_password("password")

        self.assertFalse(result)

    def test_set_password(self):
        self.player.set_password("new_pass")
        result = self.player.check_password("new_pass")

        self.assertTrue(result)
