import base64
from io import BytesIO

from fastapi import FastAPI, UploadFile
from PIL import Image
from pydantic import BaseModel

from app.image import processor
from app.response import ApiResponse

app = FastAPI(title="Image processing app")


class ClassifierOutput(BaseModel):
    score: float
    label: str


class ClassifyResponse(ApiResponse):
    data: list[ClassifierOutput]


class ObjectDectionOutput(BaseModel):

    class Box(BaseModel):
        xmin: float
        ymin: float
        xmax: float
        ymax: float

    score: float
    label: str
    box: Box


class DetectObjectResponse(ApiResponse):
    data: list[ObjectDectionOutput]


class SegmentOutput(BaseModel):
    label: str
    image: bytes


class SegmentResponse(ApiResponse):
    data: list[SegmentOutput]


def uploadfile_to_pil(upfile: UploadFile) -> Image.Image:
    return Image.open(upfile.file)


@app.get("/", response_model=ApiResponse)
async def desc():
    return ApiResponse(data={"app": "image"})


@app.post("/classify", response_model=ClassifyResponse)
async def classify(payload: UploadFile):
    img = uploadfile_to_pil(payload)
    result = await processor.classify(img)
    return ClassifyResponse(data=result)


@app.post("/detect-object", response_model=DetectObjectResponse)
async def detect_object(payload: UploadFile):
    img = uploadfile_to_pil(payload)
    result = await processor.detect(img)
    return DetectObjectResponse(data=result)


@app.post("/segment", response_model=SegmentResponse)
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
            "image": base64.b64encode(buf.getvalue())
        })
    return SegmentResponse(data=result)
