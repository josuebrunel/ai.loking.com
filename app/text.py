from fastapi import FastAPI

from app.response import ApiResponse

app = FastAPI(title="Text processing app")


@app.get("/", response_model=ApiResponse)
async def desc():
    return ApiResponse(data={"app": "text"})
