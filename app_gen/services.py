import time
from dataclasses import dataclass

import openai
from openai import OpenAIError

from decouple import config

from django.contrib.auth.models import User

from app_gen.exceptions import FailedDependencyException
from app_gen.models import ContentGenerationLog
from app_gen.messages import GenMessages

@dataclass(slots=True, frozen=True)
class GENData:
    title: str
    objective: str
    data: str
    return_format: str

class GENServices:
    """
    Service layer responsible for handling AI-powered content generation.

    It orchestrates the communication with the OpenAI API, injects a consistent persona, 
    logs generation attempts to the database, and ensures failure resilience through domain-specific exceptions.
    """
    #: Default model; can be overridden through the `OPENAI_MODEL` env var.
    _model: str = config("OPENAI_MODEL", default="gpt-4o-mini", cast=str)
    #: Temperature controls randomness;
    _temperature: float = config("OPENAI_TEMPERATURE", default=0.7, cast=float)
    #: Upper bound on latency so that API requests don’t hang indefinitely.
    _timeout: int = config("OPENAI_TIMEOUT", default=30, cast=int)
    #: Persona injected as *system* message so the behaviour remains consistent.
    _SYSTEM_PROMPT: str = (
        "Você é um assistente de RH especialista em gestão de competências, "
        "descrições de cargo, feedbacks e PDIs (Planos de Desenvolvimento "
        "Individual). Sempre responda no idioma do usuário e siga exatamente o "
        "formato pedido."
    )

    @classmethod
    def generate(cls, data: GENData, user: User) -> dict[str, str | int]:
        """
        Sends a structured prompt to the OpenAI API and returns the generated response.

        Args:
            data (GENData): Structured input containing metadata and generation parameters.
            user (User): The Django user initiating the request, used for logging.

        Returns:
            dict[str, str | int]: A dictionary containing the model used, timestamp of creation, 
                                  and the generated content.

        Raises:
            FailedDependencyException: If an error occurs during the API call to OpenAI.
        """
        openai.api_key = config("OPENAI_API_KEY")

        messages: list[dict[str, str]] = cls._build_messages(data)

        try:
            response = openai.chat.completions.create(
                model=cls._model,
                messages=messages,
                temperature=cls._temperature,
                timeout=cls._timeout,
            )
        except OpenAIError as exc:
            # Map *any* provider failure to a domain-specific exception that the
            # view knows how to translate into the proper HTTP code.
            raise FailedDependencyException(GenMessages.FAILED_DEPENDENCY) from exc

        choice: str = response.choices[0].message.content.strip()

        # Persist metadata about the generation attempt.
        ContentGenerationLog.objects.create(
            title=data.title,
            objective=data.objective,
            data=data.data,
            return_format=data.return_format,
            response=choice,
            model_used=cls._model,
            temperature=cls._temperature,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            created_by=user,
        )

        return {
            "model": response.model,
            "created": int(time.time()),
            "generated_content": choice,
        }

    @classmethod
    def _build_messages(cls, data: GENData) -> list[dict[str, str]]:
        """
        Constructs a list of chat messages conforming to the OpenAI Chat Completions API format.

        Includes a system prompt to set the assistant's behavior and a user message with 
        the generation instructions.

        Args:
            data (GENData): The input specification used to form the user message.

        Returns:
            list[dict[str, str]]: List of messages to be passed to the OpenAI API.
        """
        user_prompt: str = (
            f"Título: {data.title}\n"
            f"Objetivo: {data.objective}\n"
            f"Dados:\n{data.data}\n\n"
            f"Formato de retorno: {data.return_format}"
        )
        return [
            {"role": "system", "content": cls._SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]