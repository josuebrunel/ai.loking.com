from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.text import processors
from app.response import ApiResponse

app = FastAPI(title="Text processing app")


class Text(BaseModel):
    text: str


@app.get("/", response_model=ApiResponse)
async def desc():
    return ApiResponse(data={"app": "text"})


@app.post("/classify", response_model=ApiResponse)
async def classify(payload: list[Text], ctype: str = "default"):
    text = [p.text for p in payload]
    result = await processors.classify(text, ctype)
    return ApiResponse(data=result)
