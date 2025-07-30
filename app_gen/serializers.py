from rest_framework import serializers

from app_gen.services import GENData

from decouple import config

class GENSerializer(serializers.Serializer):
    """
    Serializer for handling content generation input.

    This serializer validates the structure of fields required for AI-driven content generation 
    and transforms the result into a strongly-typed `GENData` object for use by the generation service.
    """

    title = serializers.CharField(
        max_length=config("TITLE_MAX_LENGTH", cast=int),
        required=True,
    )
    objective = serializers.CharField(
        max_length=config("OBJECTIVE_MAX_LENGTH", cast=int),
        required=True,
    )
    data = serializers.CharField(
        max_length=config("DATA_MAX_LENGTH", cast=int),
        required=True,
    )
    return_format = serializers.CharField(
        max_length=config("RETURN_MAX_LENGTH", cast=int),
        required=True,
    )

    def validate(self, attrs: dict) -> GENData:
        """
        Converts validated data into a `GENData` object for the service layer.

        Args:
            attrs (dict): The validated input fields.

        Returns:
            GENData: Structured input for the generation service.
        """
        return GENData(**attrs)
