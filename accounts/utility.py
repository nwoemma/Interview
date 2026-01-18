import random
import string
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from django.utils import timezone
from datetime import timedelta
def generate_username(email):
    """
    Generate a unique username from email
    """
    base_username = email.split('@')[0]
    username = base_username
    while True:
        if not User.objects.filter(username=username).exists():
            return username
        username = f"{base_username}{random.randint(100, 999)}"