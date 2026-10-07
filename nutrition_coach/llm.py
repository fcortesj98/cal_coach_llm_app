"""Thin client for a vision-capable chat model on IBM watsonx.ai."""

from __future__ import annotations

import logging
from typing import Protocol

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters

from .config import WatsonxSettings
from .images import EncodedImage

logger = logging.getLogger(__name__)


class VisionModel(Protocol):
    """Anything that can answer a prompt about an image (lets tests use a fake)."""

    def ask(self, prompt: str, image: EncodedImage) -> str: ...


class WatsonxVisionModel:
    def __init__(self, settings: WatsonxSettings | None = None):
        settings = settings or WatsonxSettings()
        params = {
            key: value
            for key, value in {
                "temperature": settings.temperature,
                "top_p": settings.top_p,
                "max_tokens": settings.max_tokens,
            }.items()
            if value is not None
        }
        self.model = ModelInference(
            model_id=settings.model_id,
            credentials=Credentials(url=settings.url, api_key=settings.api_key),
            project_id=settings.project_id,
            params=TextChatParameters(**params),
        )
        logger.info("Using watsonx.ai model %s", settings.model_id)

    def ask(self, prompt: str, image: EncodedImage) -> str:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image.data_url}},
                ],
            }
        ]
        response = self.model.chat(messages=messages)
        return response["choices"][0]["message"]["content"]
