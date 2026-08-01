# uncompyle6 version 3.9.3
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
# [Clang 6.0 (clang-600.0.57)]
# Embedded file name: /Users/jayesh/Documents/Copit Me/alertsify/users/models.py
# Compiled at: 2026-05-08 15:52:23
# Size of source mod 2**32: 442 bytes
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    MODE_CHOICES = [
     ('subscriber', 'Subscriber'), ('publisher', 'Publisher')]
    preferred_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="subscriber")

    def __str__(self):
        return self.email

# okay decompiling ./users/__pycache__/models.cpython-37.pyc
