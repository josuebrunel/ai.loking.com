import os

from fastapi import FastAPI

from app.settings import settings

from app.audio import app as audio_app
from app.image import app as image_app
from app.text import app as text_app
from app.video import app as video_app


def get_app():
    return FastAPI(
        debug=settings.DEBUG,
        title="LokingAI",
        version="0.0.1",
    )


app = get_app()

app.mount("/audio", audio_app)
app.mount("/image", image_app)
app.mount("/text", text_app)
app.mount("/video", video_app)
