from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.views import exception_handler, Response
from rest_framework import status

class CustomExceptionHandler:
    @staticmethod
    def handler(exc: Exception, context: dict) -> Response:
        """
        Custom exception handler for the Django REST framework.

        This handler standardizes error responses by:
        - Replacing the default 'detail' field with a 'message' key for consistency.
        - Intercepting JWT-related errors (e.g., invalid or expired tokens) and returning a simplified, user-friendly message.

        Args:
            exc (Exception): The exception raised.
            context (dict): The context in which the exception occurred.
        """
        response = exception_handler(exc, context)

        if isinstance(exc, (InvalidToken, TokenError)):
            response = Response(
                {"message": "The provided token is invalid or has expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if response is not None and 'detail' in response.data:
            data: dict = response.data
            response.data['message'] = data.pop('detail')

        return response

# Expose the custom exception handler to be used in the Django settings
custom_exception_handler = CustomExceptionHandler.handler