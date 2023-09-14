from typing import List

from fastapi import FastAPI, UploadFile, HTTPException

from pdf2image import convert_from_bytes
from PIL import Image

from app.document import processor
from app.response import ApiResponse
from app.settings import settings
from app.logging import get_logger

logger = get_logger()

app = FastAPI(title="Document processing app")

CONTENT_TYPE_PDF = "application/pdf"


def validate_file(file: UploadFile) -> UploadFile:
    if file.content_type not in settings.DOCUMENT_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="invalid file type")
    if file.size / (1024 * 1024) > settings.DOCUMENT_MAXSIZE:
        raise HTTPException(status_code=400, detail="file size above limit")
    return file


@app.get("/", response_model=ApiResponse)
def desc():
    return ApiResponse({"desc": "Document processing app"})


@app.post("/answer-questions")
async def answer_questions(payload: UploadFile, questions: List):
    payload = validate_file(payload)
    img = None
    if payload.content_type == CONTENT_TYPE_PDF:
        img_list = None
        try:
            img_list = convert_from_bytes(payload.file.read(),
                                          single_file=True)
        except (ValueError) as exc:
            logger.error(exc)
            raise HTTPException(status_code=500,
                                detail="error while processing document")
        img = img_list[0]
    else:
        img = Image.open(payload.file)

    result = await processor.answer_question(img, questions)
    return ApiResponse(data=result)
