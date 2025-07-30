from rest_framework import serializers
from app_auth.services import LoginData, RefreshTokenData

class LoginSerializer(serializers.Serializer):
    """
    Serializer for handling user login input.
    
    This serializer validates the presence and type of login fields,
    and transforms the validated data into a strongly-typed LoginData
    instance for use in the service layer.

    The username and password min lengths are deliberately not set here,
    but they are 3 and 8 characters respectively for user creation.
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128)

    def validate(self, attrs: dict) -> LoginData:
        """
        Converts validated data into a LoginData object for the service layer.
        """
        return LoginData(**attrs)

class LogoutSerializer(serializers.Serializer):
    """
    Serializer for handling user logout input.

    This serializer validates the presence of a `refresh_token` field 
    and transforms the data into a strongly-typed `RefreshTokenData` object 
    for use in the service layer during logout operations.
    """
    refresh_token = serializers.CharField()

    def validate(self, attrs: dict) -> RefreshTokenData:
        """
        Converts validated data into a `RefreshTokenData` object for the service layer.

        Args:
            attrs (dict): The validated input data.

        Returns:
            RefreshTokenData: Structured representation of the logout request.
        """
        return RefreshTokenData(**attrs)

class RefreshTokenSerializer(serializers.Serializer):
    """
    Serializer for handling refresh token input.

    This serializer validates the presence of a `refresh_token` field
    and transforms the data into a strongly-typed `RefreshTokenData` object
    for use in the service layer during token refresh operations.
    """
    refresh_token = serializers.CharField()

    def validate(self, attrs: dict) -> RefreshTokenData:
        """
        Converts validated data into a `RefreshTokenData` object for the service layer.

        Args:
            attrs (dict): The validated input data.

        Returns:
            RefreshTokenData: Structured token refresh request.
        """
        return RefreshTokenData(**attrs)
