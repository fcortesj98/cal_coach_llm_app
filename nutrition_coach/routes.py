"""HTTP routes: one page that takes a meal photo and shows the nutrition analysis."""

from __future__ import annotations

import logging

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from .formatting import to_html
from .images import InvalidImageError, encode_upload
from .prompts import DEFAULT_QUESTION, build_prompt

logger = logging.getLogger(__name__)

bp = Blueprint("coach", __name__)


@bp.get("/")
def index():
    return render_template("index.html", user_query=DEFAULT_QUESTION)


@bp.post("/")
def analyze():
    user_query = request.form.get("user_query", "").strip() or DEFAULT_QUESTION
    uploaded = request.files.get("file")

    if not uploaded:
        flash("Please upload an image file.", "danger")
        return redirect(url_for("coach.index"))

    try:
        image = encode_upload(uploaded.stream)
    except InvalidImageError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("coach.index"))

    try:
        answer = current_app.extensions["vision_model"].ask(build_prompt(user_query), image)
    except Exception:
        logger.exception("Model request failed")
        flash("The AI model could not analyze this image. Please try again.", "danger")
        return redirect(url_for("coach.index"))

    return render_template(
        "index.html",
        user_query=user_query,
        response=to_html(answer),
        image_url=image.data_url,
    )


@bp.app_errorhandler(413)
def too_large(_error):
    limit = current_app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
    flash(f"That image is too large. The limit is {limit} MB.", "danger")
    return redirect(url_for("coach.index"))
