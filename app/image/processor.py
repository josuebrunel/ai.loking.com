from transformers import pipeline


async def classify(img):
    pipe = pipeline("image-classification", model="microsoft/resnet-50")
    result = pipe(img)
    return result
