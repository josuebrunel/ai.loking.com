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


@app.get("/", response_model=ApiResponse)
async def desc():
    return ApiResponse(data={"app": "text"})


@app.post("/classify", response_model=ApiResponseList)
async def classify(payload: list[Text], ctype: str = "default"):
    text = [p.text for p in payload]
    result = await processors.classify(text, ctype)
    return ApiResponse(data=result)


@app.post("/summarize", response_model=ApiResponse)
async def summarize(payload: Text):
    text = payload.text
    result = await processors.summarize(text)
    return ApiResponse(data=result[0])
