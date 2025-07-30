import re

from rest_framework import serializers

from app_users.services import UserData
from app_users.messages import UserMessages

class UserSerializer(serializers.Serializer):
    """
    Serializer for user creation and update operations.

    This serializer validates user fields and enforces a strong password policy,
    then converts the data into a strongly-typed `UserData` object for the service layer.
    """
    username = serializers.CharField(min_length=3, max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=128)

    def validate_password(self, value: str) -> str:
        """
        Validates that the password contains:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Args:
            value (str): The input password string.

        Returns:
            str: The validated password.

        Raises:
            serializers.ValidationError: If any password requirement is unmet.
        """
        errors = []

        if not re.search(r"[A-Z]", value):
            errors.append(UserMessages.PASSWORD_MISSING_UPPER)
        if not re.search(r"[a-z]", value):
            errors.append(UserMessages.PASSWORD_MISSING_LOWER)
        if not re.search(r"\d", value):
            errors.append(UserMessages.PASSWORD_MISSING_DIGIT)
        if not re.search(r"[^\w\s]", value):
            errors.append(UserMessages.PASSWORD_MISSING_SPECIAL)

        if errors:
            raise serializers.ValidationError(errors)

        return value

    def validate(self, attrs: dict) -> UserData:
        """
        Converts validated data into a `UserData` object for the service layer.

        Args:
            attrs (dict): The validated input fields.

        Returns:
            UserData: Structured user data for creation or update operations.
        """
        return UserData(**attrs)