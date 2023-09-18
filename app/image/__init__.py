import base64
from io import BytesIO

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi_redis_cache import cache
from PIL import Image
from pydantic import BaseModel

from app.image import processor
from app.response import ApiResponse
from app.settings import settings

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


def validate_file(file: UploadFile) -> UploadFile:
    if file.content_type not in settings.IMAGE_CTYPES:
        raise HTTPException(status_code=400, detail="invalid file type")
    if file.size / (1024 * 1024) > settings.IMAGE_MAXSIZE:
        raise HTTPException(status_code=400, detail="file size above limit")


def uploadfile_to_pil(upfile: UploadFile) -> Image.Image:
    validate_file(upfile)
    return Image.open(upfile.file)


@app.get("/", response_model=ApiResponse)
async def desc():
    """
    Get application description.

    Returns a simple response containing the description of the application.

    Returns:
    - **ApiResponse**: A response containing the application description.

    Example Response:
    ```
    {
        "data": {
            "app": "image"
        }
    }
    ```
    """
    return ApiResponse(data={"app": "image"})


@app.post("/classify", response_model=ClassifyResponse)
@cache(expire=30)
async def classify(payload: UploadFile):
    """
    Image classification.

    Classify an uploaded image using an image classification model.

    Parameters:
    - **payload**: The uploaded image file.

    Returns:
    - **ClassifyResponse**: A response containing classification results for the uploaded image.

    Example Response:
    ```
    {
        "data": [
            {"score": 0.85, "label": "cat"},
            {"score": 0.73, "label": "dog"}
        ]
    }
    ```
    """
    img = uploadfile_to_pil(payload)
    result = await processor.classify(img)
    return ClassifyResponse(data=result)


@app.post("/detect-object", response_model=DetectObjectResponse)
@cache(expire=30)
async def detect_object(payload: UploadFile):
    """
    Object detection.

    Detect objects in an uploaded image.

    Parameters:
    - **payload**: The uploaded image file.

    Returns:
    - **DetectObjectResponse**: A response containing object detection results for the uploaded image.

    Example Response:
    ```
    {
        "data": [
            {"score": 0.85, "label": "cat", "box": {"xmin": 0.1, "ymin": 0.2, "xmax": 0.9, "ymax": 0.8}},
            {"score": 0.73, "label": "dog", "box": {"xmin": 0.2, "ymin": 0.3, "xmax": 0.8, "ymax": 0.7}}
        ]
    }
    ```
    """
    img = uploadfile_to_pil(payload)
    result = await processor.detect(img)
    return DetectObjectResponse(data=result)


@app.post("/segment", response_model=SegmentResponse)
@cache(expire=30)
async def segment(payload: UploadFile):
    """
    Image segmentation.

    Segment an uploaded image into different regions.

    Parameters:
    - **payload**: The uploaded image file.

    Returns:
    - **SegmentResponse**: A response containing image segmentation results for the uploaded image.

    Example Response:
    ```
    {
        "data": [
            {"label": "sky", "image": "base64_encoded_image"},
            {"label": "tree", "image": "base64_encoded_image"}
        ]
    }
    ```
    """
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
