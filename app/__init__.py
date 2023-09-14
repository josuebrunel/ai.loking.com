import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.settings import settings
from app.middleware import LoggingMiddleware

from app.audio import app as audio_app
from app.image import app as image_app
from app.text import app as text_app
from app.video import app as video_app
from app.document import app as document_app


def get_app():
    return FastAPI(
        debug=settings.DEBUG,
        title="LokingAI",
        version="0.0.1",
    )


app = get_app()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(LoggingMiddleware)

app.mount("/audio", audio_app)
app.mount("/image", image_app)
app.mount("/text", text_app)
app.mount("/video", video_app)
app.mount("/document", document_app)
