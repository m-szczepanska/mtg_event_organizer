from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class Player(models.Model):
    """What is this, what does it do, why
    """
    # TODO: add integer, autoincrementing id
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    email = models.EmailField(max_length=254, blank=False)
    _password = models.CharField(max_length=255, blank=False)  # hashed

    def check_password(self, password_plaintext):
        return check_password(password_plaintext, self._password)

    # TODO: Add validation when creating player
    def set_password(self, password_plaintext):
        password_hashed = make_password(password_plaintext)
        self._password = password_hashed
        self.save()


class League(models.Model):
    pass
