from django.contrib.auth.models import User
from django.db import IntegrityError

from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.views import APIView, Request, Response
from rest_framework import status

from app_users.services import UpdateUserData, UserServices
from app_users.exceptions import ProtectedUserException
from app_users.serializers import UserSerializer
from app_users.messages import UserMessages

from core.messages import CoreMessages

from dataclasses import asdict

import logging
logger = logging.getLogger(__name__)

class UsersView(APIView):
    """
    Handles listing and creation of user accounts.

    - `GET`: Returns a list of non-superuser accounts with minimal information.
    - `POST`: Registers a new user after validating input data.
    """
    def get(self, request: Request) -> Response:
        """
        Lists all non-superuser users in the system.

        Args:
            request (Request): The HTTP request.

        Returns:
            Response:
                - 200: List of users retrieved successfully.
                - 500: Internal error while querying users.
        """
        try:
            # Values returns ValuesQuerySet so DRF can serialize it,
            # and also provide the capability of choosing exactly which fields to return.
            users = User.objects.filter(is_superuser=False).values('id', 'username', 'email', 'is_active')
            payload = [
                {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'status': 'active' if user['is_active'] else 'inactive'
                }
                for user in users
            ]
            return Response(payload, status=status.HTTP_200_OK)
        except Exception:
            logger.critical(CoreMessages.INTERNAL_SERVER_ERROR, exc_info=True, extra={'request': request})
            payload = {'message': CoreMessages.INTERNAL_SERVER_ERROR}
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request: Request) -> Response:
        """
        Creates a new user with the provided credentials and data.

        Args:
            request (Request): The HTTP request containing user creation data.

        Returns:
            Response:
                - 201: User created successfully.
                - 400: Validation or parsing failure.
                - 409: Username already in use.
                - 500: Internal server error.
        """
        try:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            payload = UserServices.create_user(serializer.validated_data)
            return Response(payload, status=status.HTTP_201_CREATED)
        except (ParseError):
            logger.info(CoreMessages.BAD_REQUEST)
            payload = {'message': CoreMessages.BAD_REQUEST}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.info(e.detail)
            payload = {'message': e.detail}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            logger.info(UserMessages.USERNAME_TAKEN)
            payload = {'message': UserMessages.USERNAME_TAKEN}
            return Response(payload, status=status.HTTP_409_CONFLICT)
        except Exception:
            logger.critical(CoreMessages.INTERNAL_SERVER_ERROR, exc_info=True, extra={'request': request})
            payload = {'message': CoreMessages.INTERNAL_SERVER_ERROR}
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserOperationsView(APIView):
    """
    Provides user-level operations: retrieve, update, and delete by user ID.
    """
    def get(self, request: Request, user_id: str) -> Response:
        """
        Retrieves a single user’s details by their ID.

        Args:
            request (Request): The HTTP request.
            user_id (str): ID of the user to retrieve. String is due to URL routing.

        Returns:
            Response:
                - 200: User found.
                - 404: User not found.
                - 500: Internal error.
        """
        try:
            payload = UserServices.get_user(int(user_id))
            return Response(payload, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.info(UserMessages.USER_NOT_FOUND)
            payload = {'message': UserMessages.USER_NOT_FOUND}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            logger.info(CoreMessages.BAD_REQUEST)
            payload = {'message': CoreMessages.BAD_REQUEST + f" {str(e)}"}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.critical(CoreMessages.INTERNAL_SERVER_ERROR, exc_info=True, extra={'request': request})
            payload = {'message': CoreMessages.INTERNAL_SERVER_ERROR}
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request: Request, user_id: str) -> Response:
        """
        Fully updates a user's account, including password.
        All fields are required.

        Args:
            request (Request): The HTTP request with updated user data.
            user_id (str): ID of the user to update.

        Returns:
            Response:
                - 200: User updated successfully.
                - 400: Validation error.
                - 403: Attempt to update a protected (superuser) account.
                - 404: User not found.
                - 409: Username conflict.
                - 500: Internal error.
        """
        try:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = UpdateUserData(user_id=int(user_id), **asdict(serializer.validated_data))
            payload = UserServices.update_user(data)
            return Response(payload, status=status.HTTP_200_OK)
        except ParseError:
            logger.info(CoreMessages.BAD_REQUEST)
            payload = {'message': CoreMessages.BAD_REQUEST}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.info(e.detail)
            payload = {'message': e.detail}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            logger.info(CoreMessages.BAD_REQUEST)
            payload = {'message': CoreMessages.BAD_REQUEST + f" {str(e)}"}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except ProtectedUserException:
            logger.info(UserMessages.USER_PROTECTED)
            payload = {'message': UserMessages.USER_PROTECTED}
            return Response(payload, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            logger.info(UserMessages.USER_NOT_FOUND)
            payload = {'message': UserMessages.USER_NOT_FOUND}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            logger.info(UserMessages.USERNAME_TAKEN)
            payload = {'message': UserMessages.USERNAME_TAKEN}
            return Response(payload, status=status.HTTP_409_CONFLICT)
        except Exception:
            logger.critical(CoreMessages.INTERNAL_SERVER_ERROR, exc_info=True, extra={'request': request})
            payload = {'message': CoreMessages.INTERNAL_SERVER_ERROR}
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request: Request, user_id: str) -> Response:
        """
        Soft deletes a user by deactivating the account.

        Args:
            request (Request): The HTTP request.
            user_id (str): ID of the user to delete.

        Returns:
            Response:
                - 200: User deactivated.
                - 403: Attempt to delete a protected (superuser) account.
                - 404: User not found.
                - 500: Internal error.
        """
        try:
            payload = UserServices.delete_user(int(user_id))
            return Response(payload, status=status.HTTP_200_OK)
        except ValueError as e:
            logger.info(CoreMessages.BAD_REQUEST)
            payload = {'message': CoreMessages.BAD_REQUEST + f" {str(e)}"}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except ProtectedUserException:
            logger.info(UserMessages.USER_PROTECTED)
            payload = {'message': UserMessages.USER_PROTECTED}
            return Response(payload, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            logger.info(UserMessages.USER_NOT_FOUND)
            payload = {'message': UserMessages.USER_NOT_FOUND}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            logger.critical(CoreMessages.INTERNAL_SERVER_ERROR, exc_info=True, extra={'request': request})
            payload = {'message': CoreMessages.INTERNAL_SERVER_ERROR}
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
