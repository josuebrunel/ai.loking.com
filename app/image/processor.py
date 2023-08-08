from transformers import pipeline


async def classify(img):
    pipe = pipeline("image-classification", model="microsoft/resnet-50")
    result = pipe(img)
    return result


async def detect(img):
    pipe = pipeline("object-detection", model="facebook/detr-resnet-50")
    return pipe(img)


async def segment(img):
    pipe = pipeline("image-segmentation",
                    model="nvidia/segformer-b0-finetuned-ade-512-512")
    return pipe(img)
