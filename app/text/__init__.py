from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator

from app.text import processors
from app.response import ApiResponse, ApiResponseList

app = FastAPI(title="Text processing app")


class Text(BaseModel):
    text: str

    @validator("text")
    def text_must_be_valid(cls, v):
        if v in ("", None):
            raise ValueError("text field can't be empty")
        return v


class QuestionAnswer(BaseModel):
    text: str
    questions: list[str]


@app.get("/", response_model=ApiResponse)
async def desc():
    return ApiResponse(data={"app": "text"})


@app.post("/classify", response_model=ApiResponseList)
async def classify(payload: list[Text]):
    text = [p.text for p in payload]
    result = await processors.classify(text)
    return ApiResponse(data=result)


@app.post("/sentiment-analyze", response_model=ApiResponseList)
async def sentiment_analyze(payload: list[Text]):
    text = [p.text for p in payload]
    result = await processors.analyze_sentiment(text)
    return ApiResponse(data=result)


@app.post("/summarize", response_model=ApiResponse)
async def summarize(payload: Text):
    text = payload.text
    result = await processors.summarize(text)
    return ApiResponse(data=result[0])


@app.post("/answer-question", response_model=ApiResponse)
async def answer_question(payload: QuestionAnswer):
    answers = []
    for question in payload.questions:
        answer = await processors.answer_question(payload.text, question)
        answers.append({"question": question, "answer": answer})
    return ApiResponse(data=answers)
