from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator

from app.text import processors
from app.response import ApiResponse, ApiResponseList

app = FastAPI(title="Text processing app")


class TextRequest(BaseModel):
    text: str

    @validator("text")
    def text_must_be_valid(cls, v):
        if v in ("", None):
            raise ValueError("text field can't be empty")
        return v


class QuestionAnswerRequest(BaseModel):
    text: str
    questions: list[str]


class Answer(BaseModel):
    score: float
    start: int
    end: int
    answer: str


class QuestionAnswer(BaseModel):
    question: str
    answer: Answer


class QuestionAnswerResponse(ApiResponse):
    data: list[QuestionAnswer]


class LabelRequest(BaseModel):
    text: str
    labels: list[str]


class LabelOutput(BaseModel):
    sequence: str
    labels: list[str]
    scores: list[float]


class LabelResponse(ApiResponse):
    data: LabelOutput


@app.get("/", response_model=ApiResponse)
async def desc():
    return ApiResponse(data={"app": "text"})


@app.post("/classify", response_model=ApiResponseList)
async def classify(payload: list[TextRequest]):
    text = [p.text for p in payload]
    result = await processors.classify(text)
    return ApiResponse(data=result)


@app.post("/sentiment-analyze", response_model=ApiResponseList)
async def sentiment_analyze(payload: list[TextRequest]):
    text = [p.text for p in payload]
    result = await processors.analyze_sentiment(text)
    return ApiResponse(data=result)


@app.post("/summarize", response_model=ApiResponse)
async def summarize(payload: TextRequest):
    text = payload.text
    result = await processors.summarize(text)
    return ApiResponse(data=result[0])


@app.post("/answer-question", response_model=QuestionAnswerResponse)
async def answer_question(payload: QuestionAnswerRequest):
    answers = []
    for question in payload.questions:
        answer = await processors.answer_question(payload.text, question)
        answers.append({"question": question, "answer": answer})
    return QuestionAnswerResponse(data=answers)


@app.post("/label", response_model=LabelResponse)
async def label(payload: LabelRequest, multi_label=True):
    result = await processors.zero_shot_classify(payload.text,
                                                 payload.labels,
                                                 multi_label=multi_label)
    return LabelResponse(data=result)
