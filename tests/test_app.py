"""Tests for the Nutrition Coach. A fake model stands in for watsonx.ai."""

from io import BytesIO

import pytest
from PIL import Image

from nutrition_coach import create_app
from nutrition_coach.config import Settings
from nutrition_coach.formatting import to_html
from nutrition_coach.images import InvalidImageError, encode_upload
from nutrition_coach.prompts import DEFAULT_QUESTION, DISCLAIMER, build_prompt

SAMPLE_ANSWER = """\
1. **Identification**:
*   Burger
*   French fries

2. **Portion Size & Calorie Estimation**:
*   **Burger**: 1 sandwich, 550 calories
*   **French fries**: 1 medium serving, 365 calories

3. **Total Calories**: 915 calories

<script>alert("x")</script>
"""


def png_bytes(fmt="PNG"):
    buf = BytesIO()
    Image.new("RGB", (4, 4), "red").save(buf, format=fmt)
    return buf.getvalue()


class FakeModel:
    def __init__(self, answer=SAMPLE_ANSWER, error=None):
        self.answer, self.error, self.calls = answer, error, []

    def ask(self, prompt, image):
        self.calls.append((prompt, image))
        if self.error:
            raise self.error
        return self.answer


@pytest.fixture
def make_client():
    def _make(model=None, **settings):
        app = create_app(Settings(**settings), model=model or FakeModel())
        app.config["TESTING"] = True
        return app.test_client(), app.extensions["vision_model"]

    return _make


def test_encode_upload_detects_mime_type():
    assert encode_upload(BytesIO(png_bytes("PNG"))).mime_type == "image/png"
    jpeg = encode_upload(BytesIO(png_bytes("JPEG")))
    assert jpeg.data_url.startswith("data:image/jpeg;base64,")


@pytest.mark.parametrize("payload", [b"", b"not an image"])
def test_encode_upload_rejects_bad_files(payload):
    with pytest.raises(InvalidImageError):
        encode_upload(BytesIO(payload))


def test_build_prompt():
    prompt = build_prompt("  ")
    assert prompt.endswith(DEFAULT_QUESTION)
    assert DISCLAIMER in prompt
    assert build_prompt("Is this healthy?").endswith("Is this healthy?")


def test_to_html_renders_lists_and_escapes_html():
    html = to_html(SAMPLE_ANSWER)
    assert "<strong>Burger</strong>: 1 sandwich, 550 calories" in html
    assert "<li>" in html and "<ol>" in html
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_get_index(make_client):
    client, _ = make_client()
    res = client.get("/")
    assert res.status_code == 200
    assert b"AI Nutrition Coach" in res.data
    assert DEFAULT_QUESTION.encode() in res.data


def test_post_analyzes_image(make_client):
    client, model = make_client()
    res = client.post(
        "/",
        data={"user_query": "Is this healthy?", "file": (BytesIO(png_bytes()), "meal.png")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 200
    assert b"915 calories" in res.data
    assert b'src="data:image/png;base64,' in res.data
    prompt, image = model.calls[0]
    assert prompt.endswith("Is this healthy?") and image.mime_type == "image/png"


def test_post_without_file_flashes_error(make_client):
    client, model = make_client()
    res = client.post("/", data={"user_query": "hi"}, follow_redirects=True)
    assert b"Please upload an image file." in res.data
    assert model.calls == []


def test_post_invalid_image_flashes_error(make_client):
    client, _ = make_client()
    res = client.post(
        "/",
        data={"file": (BytesIO(b"hello"), "notes.txt")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"not a valid image" in res.data


def test_model_failure_is_handled(make_client):
    client, _ = make_client(model=FakeModel(error=RuntimeError("boom")))
    res = client.post(
        "/",
        data={"file": (BytesIO(png_bytes()), "meal.png")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"could not analyze this image" in res.data


def test_upload_size_limit(make_client):
    client, _ = make_client(max_upload_mb=1)
    big = BytesIO(b"0" * (2 * 1024 * 1024))
    res = client.post(
        "/",
        data={"file": (big, "huge.png")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"too large" in res.data
