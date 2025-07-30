from rest_framework.views import Request, Response
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.views import APIView
from rest_framework import status

from app_gen.exceptions import FailedDependencyException
from app_gen.serializers import GENSerializer
from app_gen.services import GENServices
from app_gen.messages import GenMessages

from core.messages import CoreMessages

import logging
logger = logging.getLogger(__name__)

class GenView(APIView):
    """
    Handles content generation requests using the GEN service.

    This endpoint receives structured data, validates the input using `GENSerializer`, and delegates 
    the request to `GENServices.generate`. It returns the generated content or a meaningful error response.

    Typical use case involves AI-generated outputs such as feedbacks, job descriptions, or development plans.
    """
    def post(self, request: Request) -> Response:
        """
        Processes a POST request to generate content based on validated input data.

        Args:
            request (Request): The HTTP request containing the generation payload. Must include valid structured JSON.

        Returns:
            Response:
                - 200: Successfully generated content.
                - 400: Malformed input or validation failure.
                - 424: Dependency failure during generation (e.g., external service error).
                - 500: Internal server error for unhandled exceptions.
        """
        try:
            serializer = GENSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            payload = GENServices.generate(serializer.validated_data, request.user)
            return Response(payload, status=status.HTTP_200_OK)
        except ParseError:
            logger.info(CoreMessages.BAD_REQUEST)
            payload = {'message': CoreMessages.BAD_REQUEST}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.info(e.detail)
            payload = {'message': e.detail}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        except FailedDependencyException:
            logger.info(GenMessages.FAILED_DEPENDENCY)
            payload = {'message': GenMessages.FAILED_DEPENDENCY}
            return Response(payload, status=status.HTTP_424_FAILED_DEPENDENCY)
        except Exception:
            logger.critical(CoreMessages.INTERNAL_SERVER_ERROR, exc_info=True, extra={'request': request})
            payload = {'message': CoreMessages.INTERNAL_SERVER_ERROR}
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
