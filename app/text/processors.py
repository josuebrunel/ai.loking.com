from transformers import pipeline


async def classify(text):
    pipe = pipeline("text-classification",
                    model="distilbert-base-uncased-finetuned-sst-2-english")
    result = pipe(text)
    return result


async def analyze_sentiment(text):
    pipe = pipeline("text-classification",
                    model="SamLowe/roberta-base-go_emotions")
    result = pipe(text)
    return result


async def summarize(text):
    pipe = pipeline("summarization", model="facebook/bart-large-cnn")
    return pipe(text)


async def answer_question(text, question):
    pipe = pipeline("question-answering", model="deepset/roberta-base-squad2")
    result = pipe({"question": question, "context": text})
    return result
