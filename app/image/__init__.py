import base64
from io import BytesIO

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel

from app.image import processor
from app.response import ApiResponse, ApiResponseList

app = FastAPI(title="Image processing app")


class Payload(BaseModel):
    b64content: str | None = None


@app.get("/", response_model=ApiResponse)
async def desc():
    return ApiResponse(data={"app": "image"})


@app.post("/classify", response_model=ApiResponseList)
async def classify(payload: Payload):
    buf = BytesIO(base64.b64decode(payload.b64content))
    img = Image.open(buf)
    result = await processor.classify(img)
    return ApiResponseList(data=result)
