import re
from django.core.exceptions import ValidationError


# This class is for checking the strength of the password when the user registers.
class StrongPasswordValidator:
    def __init__(self, min_length):
        self.min_length = min_length

    def validate(self, password, user=None):

        # Check the minimum number of password characters
        if len(password) < self.min_length:
            raise ValidationError(
                "The password must be at least %(min_length)d characters long."
                % {"min_length": self.min_length},
                code="password_too_short",
            )

        # Check for having at least one uppercase letter
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                "The password must contain at least one uppercase letter (A-Z)",
                code="password_no_upper",
            )

        # Checking for the presence of at least one number
        if not re.search(r"\d", password):
            raise ValidationError(
                "The password must contain at least one number.",
                code="password_no_number",
            )

        # The presence of one of the characters (!@#$%&*)
        if not re.search(r"[@$!%*?&]", password):
            raise ValidationError(
                "The password must contain at least one special character such as @#$%&*",
                code="password_no_special",
            )
