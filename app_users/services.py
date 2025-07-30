from django.contrib.auth.models import User

from app_users.messages import UserMessages
from app_users.exceptions import ProtectedUserException

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class UserData:
    username: str
    email: str
    password: str

@dataclass(frozen=True, slots=True)
class CreateUserData(UserData):
    pass

@dataclass(frozen=True, slots=True)
class UpdateUserData(UserData):
    user_id: int

class UserServices:
    """
    Service layer for business logic related to user management.
    Encapsulates operations for creation, retrieval, update, and soft deletion of users.
    """
    @staticmethod
    def create_user(data: CreateUserData) -> dict:
        """
        Creates a new user using the provided validated data.

        Args:
            data (CreateUserData): Structured data containing username, email, and password.

        Returns:
            dict: Confirmation message.

        Raises:
            IntegrityError: If the username already exists.
        """
        User.objects.create_user(
            username=data.username,
            email=data.email,
            password=data.password
        )
        return {'message': UserMessages.USER_CREATED}

    @staticmethod
    def get_user(user_id: int) -> dict:
        """
        Fetches user details by ID.

        Args:
            user_id (int): ID of the user to retrieve.

        Returns:
            dict: Dictionary with user attributes.

        Raises:
            User.DoesNotExist: If the user ID is invalid.
            ValueError: If the user ID is less than or equal to zero.
        """
        if user_id <= 0:
            raise ValueError(UserMessages.INVALID_USER_ID)

        user = User.objects.get(id=user_id)
        return {
            'id': user.pk,
            'username': user.username,
            'email': user.email,
            'status': 'active' if user.is_active else 'inactive'
        }

    @staticmethod
    def update_user(data: UpdateUserData) -> dict:
        """
        Performs a full update of the user's information.

        Args:
            data (UpdateUserData): Contains new values and the user ID.

        Returns:
            dict: Success message.

        Raises:
            User.DoesNotExist: If the user doesn't exist.
            ProtectedUserException: If attempting to update a superuser account.
            ValueError: If the user ID is less than or equal to zero.
        """
        if data.user_id <= 0:
            raise ValueError(UserMessages.INVALID_USER_ID)
        user = User.objects.get(id=data.user_id)
        if user.is_superuser:
            raise ProtectedUserException()
        user.username = data.username
        user.email = data.email
        user.set_password(data.password)
        user.save()
        return {'message': UserMessages.USER_UPDATED}

    @staticmethod
    def delete_user(user_id: int) -> dict:
        """
        Performs a soft delete by setting the user as inactive.

        Args:
            user_id (int): ID of the user to deactivate.

        Returns:
            dict: Deletion success message.

        Raises:
            User.DoesNotExist: If the user doesn't exist.
            ProtectedUserException: If the user is protected from deletion.
            ValueError: If the user ID is less than or equal to zero.
        """
        if user_id <= 0:
            raise ValueError(UserMessages.INVALID_USER_ID)
        user = User.objects.get(id=user_id)
        if user.is_superuser:
            raise ProtectedUserException()
        user.is_active = False
        user.save()
        return {'message': UserMessages.USER_DELETED}
