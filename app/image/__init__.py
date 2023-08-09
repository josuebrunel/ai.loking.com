import base64
from io import BytesIO

from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel

from app.image import processor
from app.response import ApiResponse, ApiResponseList

app = FastAPI(title="Image processing app")


def uploadfile_to_pil(upfile: UploadFile) -> Image.Image:
    return Image.open(upfile.file)


@app.get("/", response_model=ApiResponse)
async def desc():
    return ApiResponse(data={"app": "image"})


@app.post("/classify", response_model=ApiResponseList)
async def classify(payload: UploadFile):
    img = uploadfile_to_pil(payload)
    result = await processor.classify(img)
    return ApiResponseList(data=result)


@app.post("/detect-object", response_model=ApiResponseList)
async def detect_object(payload: UploadFile):
    img = uploadfile_to_pil(payload)
    result = await processor.detect(img)
    return ApiResponseList(data=result)


@app.post("/segment", response_model=ApiResponseList)
async def segment(payload: UploadFile):
    if not payload:
        return ApiResponse(error="no-file-sent")
    img = uploadfile_to_pil(payload)
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
