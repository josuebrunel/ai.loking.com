from transformers import pipeline

MODELS = {
    "classify": {
        "default": "distilbert-base-uncased-finetuned-sst-2-english",
        "emotions": "SamLowe/roberta-base-go_emotions"
    }
}


async def classify(text, ctype="default"):
    pipe = pipeline("text-classification",
                    model=MODELS["classify"].get(ctype, "default"))
    result = pipe(text)
    return result
