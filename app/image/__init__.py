import base64
from io import BytesIO

from fastapi import FastAPI, UploadFile
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


@app.post("/detect", response_model=ApiResponseList)
async def detect(payload: Payload):
    buf = BytesIO(base64.b64decode(payload.b64content))
    img = Image.open(buf)
    result = await processor.detect(img)
    return ApiResponseList(data=result)


@app.post("/segmenter", response_model=ApiResponseList)
async def segmenter(image: UploadFile):
    if not image:
        return ApiResponse(error="no-file-sent")
    img = Image.open(image.file)
    img_format = img.format
    segments = await processor.segment(img)
    result = []
    for segment in segments:
        buf = BytesIO()
        pil_img = segment["mask"]
        pil_img.save(buf, format=img_format)
        result.append({
            "label": segment["label"],
            "img": base64.b64encode(buf.getvalue())
        })
    return ApiResponseList(data=result)
