from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken

from app_users.exceptions import InvalidCredentialsException, InactiveUserException

from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class LoginData:
    username: str
    password: str

@dataclass(slots=True, frozen=True)
class RefreshTokenData:
    refresh_token: str

class AuthServices:
    @staticmethod
    def login(data: LoginData) -> dict:
        """
        Authenticate the user and generate JWT tokens.

        Args:
            data (LoginData): User credentials.

        Returns:
            dict: Access and refresh tokens.

        Raises:
            InvalidCredentialsException: If authentication fails.
            InactiveUserException: If the user account is inactive.
        """
        print(type(data), data)

        user = authenticate(username=data.username, password=data.password)
        if user is None:
            raise InvalidCredentialsException()
        
        if not user.is_active:
            raise InactiveUserException()

        refresh = RefreshToken.for_user(user)

        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }

    @staticmethod
    def logout(data: RefreshTokenData) -> dict:
        """
        Blacklist the refresh token to invalidate it.

        Args:
            data (RefreshTokenData): Refresh token to be blacklisted.

        Returns:
            dict: Confirmation message.
        """
        token = RefreshToken(data.refresh_token)
        token.blacklist()

        return {"message": "Refresh token blacklisted successfully."}

    @staticmethod
    def refresh_token(data: RefreshTokenData) -> dict:
        """
        Generate a new access token using the provided refresh token.

        Args:
            data (RefreshTokenData): Refresh token to generate a new access token.

        Returns:
            dict: New access token.
        """
        token = RefreshToken(data.refresh_token)
        return {
            "access_token": str(token.access_token),
        }
