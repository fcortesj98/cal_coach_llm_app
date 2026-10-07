"""Configuration for the AI Nutrition Coach.

Defaults work inside the IBM Skills Network lab environment. Every value can
be overridden with an environment variable to run against your own
watsonx.ai account or to try a different model (lab Exercises 1 and 2).
"""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass, field


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def _env_float(name: str) -> float | None:
    value = _env(name)
    return float(value) if value is not None else None


def _env_int(name: str) -> int | None:
    value = _env(name)
    return int(value) if value is not None else None


@dataclass(frozen=True)
class WatsonxSettings:
    """watsonx.ai connection and generation settings.

    Generation parameters left as ``None`` use the model's own defaults,
    which is what the original lab did.
    """

    model_id: str = "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"
    url: str = "https://us-south.ml.cloud.ibm.com"
    # The lab environment injects credentials, so no key is needed there.
    api_key: str | None = None
    project_id: str = "skills-network"
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None

    @classmethod
    def from_env(cls) -> "WatsonxSettings":
        return cls(
            model_id=_env("WATSONX_MODEL_ID", cls.model_id),
            url=_env("WATSONX_URL", cls.url),
            api_key=_env("WATSONX_APIKEY"),
            project_id=_env("WATSONX_PROJECT_ID", cls.project_id),
            temperature=_env_float("WATSONX_TEMPERATURE"),
            top_p=_env_float("WATSONX_TOP_P"),
            max_tokens=_env_int("WATSONX_MAX_TOKENS"),
        )


@dataclass(frozen=True)
class Settings:
    """Top-level application settings."""

    # Needed by Flask to show flash messages. A random key is fine for local use.
    secret_key: str = field(default_factory=lambda: secrets.token_hex(16))
    # Reject uploads larger than this (Flask returns 413).
    max_upload_mb: int = 10
    watsonx: WatsonxSettings = field(default_factory=WatsonxSettings)

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            secret_key=_env("FLASK_SECRET_KEY") or secrets.token_hex(16),
            max_upload_mb=int(_env("MAX_UPLOAD_MB", "10")),
            watsonx=WatsonxSettings.from_env(),
        )
