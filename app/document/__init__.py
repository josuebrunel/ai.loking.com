from typing import Annotated, List

from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi_redis_cache import cache
from pdf2image import convert_from_bytes
from PIL import Image
from pydantic import BaseModel

from app.document import processor
from app.logger import logger
from app.response import ApiResponse
from app.settings import settings

app = FastAPI(title="Document processing app")

CONTENT_TYPE_PDF = "application/pdf"


class DocumentQuestionAnswer(BaseModel):
    question: str
    answer: str
    score: float
    start: int
    end: int


class DocumentQuestionAnswerResponse(ApiResponse):
    data: List[DocumentQuestionAnswer]


def validate_file(file: UploadFile) -> UploadFile:
    """
    Validate an uploaded file based on content type and size.

    Parameters:
    - **file**: The uploaded file.

    Returns:
    - **UploadFile**: The validated file.

    Raises:
    - **HTTPException**: If the file type or size is invalid.
    """
    if file.content_type not in settings.DOCUMENT_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="invalid file type")
    if file.size / (1024 * 1024) > settings.DOCUMENT_MAXSIZE:
        raise HTTPException(status_code=400, detail="file size above limit")
    return file


@app.get("/", response_model=ApiResponse)
@cache(expire=30)
def desc():
    """
    Get application description.

    Returns a simple response containing the description of the application.

    Returns:
    - **ApiResponse**: A response containing the application description.

    Example Response:
    ```
    {
        "data": {
            "desc": "Document processing app"
        }
    }
    ```
    """
    return ApiResponse(data={"desc": "Document processing app"})


@app.post("/answer-questions", response_model=DocumentQuestionAnswerResponse)
async def answer_questions(payload: UploadFile, questions: Annotated[str,
                                                                     Form()]):
    """
    Answer questions based on an uploaded document.

    This endpoint takes an uploaded document file and a list of questions. It processes the document
    to find answers to the questions.

    Parameters:
    - **payload**: The uploaded document file.
    - **questions**: A comma-separated list of questions.

    Returns:
    - **DocumentQuestionAnswerResponse**: A response containing answers to the questions.

    Example Request:
    ```
    POST /answer-questions
    Content-Type: multipart/form-data
    Body: <Upload a PDF or image file>
    Form Data: questions=Question1,Question2,Question3
    ```

    Example Response:
    ```
    {
        "data": [
            {
                "question": "Question1",
                "answer": "Answer1",
                "score": 0.85,
                "start": 10,
                "end": 20
            },
            {
                "question": "Question2",
                "answer": "Answer2",
                "score": 0.75,
                "start": 30,
                "end": 40
            },
            {
                "question": "Question3",
                "answer": "Answer3",
                "score": 0.92,
                "start": 50,
                "end": 60
            }
        ]
    }
    ```
    """
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

    result = await processor.answer_question(img, questions.split(','))
    return DocumentQuestionAnswerResponse(data=result)
