import re
import string
from rest_framework import serializers
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    def validate(self, password, user=None):
        errors = []

        # Check if a string contains uppercase letter
        if not re.search(r"[A-Z]", password):
            errors.append(_("Password must contain at least one uppercase letter."))

        # Check if a string contains lowercase letter
        if not re.search(r"[a-z]", password):
            errors.append(_("Password must contain at least one lowercase letter."))

        # Check if a string contains a number
        if not re.search(r"\d", password):
            errors.append(_("Password must contain at least one digit."))

        # Check if a string contains special character
        if not re.search(f"[{re.escape(string.punctuation)}]", password):
            errors.append(_("Password must contain at least one special character."))

        if errors:
            raise serializers.ValidationError(errors)

        return password
