"""AI Nutrition Coach: estimate calories and nutrients from a meal photo."""

from __future__ import annotations

from flask import Flask

from .config import Settings
from .llm import VisionModel


def create_app(settings: Settings | None = None, model: VisionModel | None = None) -> Flask:
    """Application factory.

    Args:
        settings: app settings; read from environment variables if omitted.
        model: vision model to use; a watsonx.ai client is created if omitted
            (tests pass a fake here).
    """
    settings = settings or Settings.from_env()

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=settings.secret_key,
        MAX_CONTENT_LENGTH=settings.max_upload_mb * 1024 * 1024,
    )

    if model is None:
        from .llm import WatsonxVisionModel

        model = WatsonxVisionModel(settings.watsonx)
    app.extensions["vision_model"] = model

    from .routes import bp

    app.register_blueprint(bp)
    return app
