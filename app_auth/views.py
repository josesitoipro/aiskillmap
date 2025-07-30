
from rest_framework_simplejwt.exceptions import TokenError

from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.views import APIView, Request, Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from app_auth.serializers import LoginSerializer, LogoutSerializer
from app_auth.serializers import RefreshTokenSerializer
from app_auth.services import AuthServices
from app_auth.messages import AuthMessages

from app_users.exceptions import InvalidCredentialsException, InactiveUserException
from core.messages import CoreMessages

import logging
logger = logging.getLogger(__name__)

class LoginView(APIView):
    """
    Handles user authentication via JWT.

    Accepts a username and password, and returns a new pair of access and refresh tokens upon successful login.
    """
    permission_classes = [AllowAny]
    def post(self, request: Request) -> Response:
        """
        Authenticates the user and returns JWT tokens, provided the credentials are valid.

        Args:
            request (Request): The HTTP request containing the login payload. Expects a JSON body with 'username' and 'password'.

        Returns:
            Response: 200 on success with JWT tokens.
                      400 if payload is malformed.
                      401 if credentials are invalid.
                      403 if the user account is inactive.
                      500 for unexpected server errors.
        """
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            payload = AuthServices.login(serializer.validated_data)
            return Response(payload, status=status.HTTP_200_OK)
        except ParseError:
            logger.info(CoreMessages.BAD_REQUEST)
            payload = {'message': CoreMessages.BAD_REQUEST}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.info(e.detail)
            payload = {'message': e.detail}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except InvalidCredentialsException:
            logger.info(AuthMessages.INVALID_CREDENTIALS)
            payload = {'message': AuthMessages.INVALID_CREDENTIALS}
            return Response(payload, status=status.HTTP_401_UNAUTHORIZED)
        except InactiveUserException:
            logger.info(AuthMessages.INACTIVE_USER)
            payload = {'message': AuthMessages.INACTIVE_USER}
            return Response(payload, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            logger.critical(CoreMessages.INTERNAL_SERVER_ERROR, exc_info=True, extra={'request': request})
            payload = {'message': CoreMessages.INTERNAL_SERVER_ERROR}
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    """
    Handles user logout by invalidating the refresh token.

    Prevents further token refresh attempts using the provided token.
    The access token remains valid until it naturally expires.
    """
    def post(self, request: Request) -> Response:
        """
        Invalidates the refresh token to end the session.

        Args:
            request (Request): The HTTP request containing the refresh token.

        Returns:
            Response: 200 response confirming token blacklisting.
                      400 if malformed input.
                      401 if the token is invalid.
                      500 for unexpected server errors.
        """
        try:
            serializer = LogoutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            payload = AuthServices.logout(serializer.validated_data)
            return Response(payload, status=status.HTTP_200_OK)
        except (ParseError, ValidationError):
            logger.info(CoreMessages.BAD_REQUEST)
            payload = {'message': CoreMessages.BAD_REQUEST}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            logger.info(AuthMessages.INVALID_TOKEN)
            payload = {'message': AuthMessages.INVALID_TOKEN}
            return Response(payload, status=status.HTTP_401_UNAUTHORIZED)
        except Exception:
            logger.critical(CoreMessages.INTERNAL_SERVER_ERROR, exc_info=True, extra={'request': request})
            payload = {'message': CoreMessages.INTERNAL_SERVER_ERROR}
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RefreshTokenView(APIView):
    """
    Provides a new access token in exchange for a valid refresh token.

    Allows users to maintain their session without re-authenticating.
    """
    def post(self, request: Request) -> Response:
        """
        Refreshes the access token using a valid refresh token.

        Args:
            request (Request): The HTTP request containing the refresh token.

        Returns:
            Response: 200 response with a new access token.
                      400 if malformed input.
                      401 if the refresh token is invalid or expired.
                      500 for unexpected server errors.
        """
        try:
            serializer = RefreshTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            payload = AuthServices.refresh_token(serializer.validated_data)
            return Response(payload, status=status.HTTP_200_OK)
        except (ParseError, ValidationError):
            logger.info(CoreMessages.BAD_REQUEST)
            payload = {'message': CoreMessages.BAD_REQUEST}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            logger.info(AuthMessages.INVALID_TOKEN)
            payload = {'message': AuthMessages.INVALID_TOKEN}
            return Response(payload, status=status.HTTP_401_UNAUTHORIZED)
        except Exception:
            logger.critical(CoreMessages.INTERNAL_SERVER_ERROR, exc_info=True, extra={'request': request})
            payload = {'message': CoreMessages.INTERNAL_SERVER_ERROR}
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)