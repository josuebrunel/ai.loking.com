from transformers import pipeline
from sentence_transformers import SentenceTransformer
import torch


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


async def mask_filler(text):
    pipe = pipeline("fill-mask", model="bert-base-uncased")
    result = pipe(text)
    return result


async def zero_shot_classify(text, labels, multi_label=True):
    classifier = pipeline("zero-shot-classification",
                          model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
    result = classifier(text, labels, multi_label=multi_label)
    return result


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[
        0]  #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(
        token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9)


async def similarities_check(sentences):
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    embeddings = model.encode(sentences)
    cos = torch.nn.CosineSimilarity(dim=0)
    result = []
    for i in range(1, len(embeddings)):
        result.append({
            "sentence":
            sentences[i],
            "score":
            cos(torch.from_numpy(embeddings[0]),
                torch.from_numpy(embeddings[i])).item()
        })
    return result
