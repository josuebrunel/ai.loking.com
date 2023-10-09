from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi_redis_cache import cache
from pydantic import BaseModel, validator

from app.response import ApiResponse, ApiResponseList
from app.text import processors

app = FastAPI(title="Text processing app")


class TextRequest(BaseModel):
    text: str

    @validator("text")
    def text_must_be_valid(cls, v):
        if v in ("", None):
            raise ValueError("text field can't be empty")
        return v


class QuestionAnswerRequest(BaseModel):
    text: str
    questions: list[str]


class Answer(BaseModel):
    score: float
    start: int
    end: int
    answer: str


class QuestionAnswer(BaseModel):
    question: str
    answer: Answer


class QuestionAnswerResponse(ApiResponse):
    data: list[QuestionAnswer]


class LabelRequest(BaseModel):
    text: str
    labels: list[str]


class LabelOutput(BaseModel):
    sequence: str
    labels: list[str]
    scores: list[float]


class LabelResponse(ApiResponse):
    data: LabelOutput


class MaskFillerOutput(BaseModel):
    score: float
    token: int
    token_str: str
    sequence: str


class MaskFillerResponse(ApiResponse):
    data: list[MaskFillerOutput]


class SentencesSimilarityResponse(ApiResponse):

    class SimilarityScore(BaseModel):
        sentence: str
        score: float

    data: list[SimilarityScore]


@app.get("/", response_model=ApiResponse)
@cache()
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
            "app": "text"
        }
    }
    ```
    """
    return ApiResponse(data={"app": "text"})


@app.post("/classifier", response_model=ApiResponseList)
@cache(expire=30)
async def classifier(payload: list[TextRequest]):
    """
    Text classification.

    Classify a list of texts using a text classification model.

    Parameters:
    - **payload**: List of TextRequest objects containing the input texts.

    Returns:
    - **ApiResponseList**: A list of responses containing classification results for each input text.

    Example Request:
    ```
    POST /classifier
    [
        {
            "text": "This is a positive review."
        },
        {
            "text": "This is a negative review."
        }
    ]
    ```

    Example Response:
    ```
    {
        "data": [
            {"label": "positive", "score": 0.85},
            {"label": "negative", "score": 0.73}
        ]
    }
    ```
    """
    text = [p.text for p in payload]
    result = await processors.classify(text)
    return ApiResponse(data=result)


@app.post("/sentiment-analyzer", response_model=ApiResponseList)
@cache(expire=30)
async def sentiment_analyzer(payload: list[TextRequest]):
    """
    Sentiment analysis.

    Analyze sentiment for a list of texts.

    Parameters:
    - **payload**: List of TextRequest objects containing the input texts.

    Returns:
    - **ApiResponseList**: A list of responses containing sentiment analysis results for each input text.

    Example Request:
    ```
    POST /sentiment-analyzer
    [
        {
            "text": "I love this product!"
        },
        {
            "text": "I'm not satisfied with the service."
        }
    ]
    ```

    Example Response:
    ```
    {
        "error": null,
        "data": [
            {
                "label": "love",
                "score": 0.9471527338027954
            },
            {
                "label": "disapproval",
                "score": 0.6938314437866211
            }
        ]
    }
    ```
    """
    text = [p.text for p in payload]
    result = await processors.analyze_sentiment(text)
    return ApiResponse(data=result)


@app.post("/summarizer", response_model=ApiResponse)
@cache(expire=30)
async def summarizer(payload: TextRequest):
    """
    Text summarization.

    Summarize the input text.

    Parameters:
    - **payload**: TextRequest object containing the input text.

    Returns:
    - **ApiResponse**: A response containing the summarized text.

    Example Request:
    ```
    POST /summarizer
    {
        "text": "This is a long piece of text..."
    }
    ```

    Example Response:
    ```
    {
        "data": {
            "summary_text": "This is a summarized version of the input text..."
        }
    }
    ```
    """
    text = payload.text
    result = await processors.summarize(text)
    return ApiResponse(data=result[0])


@app.post("/question-answering", response_model=QuestionAnswerResponse)
@cache(expire=30)
async def question_answering(payload: QuestionAnswerRequest):
    """
    Question answering.

    Answer a list of questions based on the input text.

    Parameters:
    - **payload**: QuestionAnswerRequest object containing the input text and list of questions.

    Returns:
    - **QuestionAnswerResponse**: A response containing the answers to the questions.

    Example Request:
    ```
    POST /question-answering
    {
        "text": "The capital of France is Paris and that city has a population of 2m people",
        "questions": ["What is the capital of France?", "What is the population of Paris?"]
    }
    ```

    Example Response:
    ```
    {
      "error": null,
      "data": [
        {
          "question": "What is the capital of France?",
          "answer": {
            "score": 0.9588838815689087,
            "start": 20,
            "end": 25,
            "answer": "Paris"
          }
        },
        {
          "question": "What is the population of Paris?",
          "answer": {
            "score": 0.6355919241905212,
            "start": 60,
            "end": 62,
            "answer": "2m"
          }
        }
      ]
    }
    ```
    """
    answers = []
    for question in payload.questions:
        answer = await processors.answer_question(payload.text, question)
        answers.append({"question": question, "answer": answer})
    return QuestionAnswerResponse(data=answers)


@app.post("/labelizer", response_model=LabelResponse)
@cache(expire=30)
async def labelizer(payload: LabelRequest, multi_label=True):
    """
    Text labeling.

    Label the input text with specified labels.

    Parameters:
    - **payload**: LabelRequest object containing the input text and list of labels.

    Returns:
    - **LabelResponse**: A response containing the labeled text and label scores.

    Example Request:
    ```
    POST /labelizer
    {
        "text": "This is an example sentence.",
        "labels": ["positive", "negative"]
    }
    ```

    Example Response:
    ```
    {
        "data": {
            "sequence": "This is an example sentence.",
            "labels": ["positive", "neutral"],
            "scores": [0.75, 0.2]
        }
    }
    ```
    """
    result = await processors.zero_shot_classify(payload.text,
                                                 payload.labels,
                                                 multi_label=multi_label)
    return LabelResponse(data=result)


@app.post("/mask-filler", response_model=MaskFillerResponse)
@cache(expire=30)
async def mask_filler(payload: TextRequest):
    """
    Mask filling.

    Fill in masked values in the input text.

    Parameters:
    - **payload**: TextRequest object containing the input text with masked values.

    Returns:
    - **MaskFillerResponse**: A response containing the filled-in masked values.

    Example Request:
    ```
    POST /mask-filler
    {
        "text": "Please buy [MASK] from the store."
    }
    ```

    Example Response:
    ```
    {
      "error": null,
      "data": [
        {
          "score": 0.17938034236431122,
          "token": 2505,
          "token_str": "anything",
          "sequence": "please buy anything from this store"
        },
        {
          "score": 0.11332187056541443,
          "token": 2242,
          "token_str": "something",
          "sequence": "please buy something from this store"
        },
        {
          "score": 0.05946308374404907,
          "token": 3688,
          "token_str": "products",
          "sequence": "please buy products from this store"
        },
        {
          "score": 0.04591205716133118,
          "token": 5167,
          "token_str": "items",
          "sequence": "please buy items from this store"
        },
        {
          "score": 0.04386703670024872,
          "token": 2009,
          "token_str": "it",
          "sequence": "please buy it from this store"
        }
      ]
    }
    ```
    """
    result = await processors.mask_filler(payload.text)
    return MaskFillerResponse(data=result)


@app.post("/similarities-detector", response_model=SentencesSimilarityResponse)
@cache(expire=30)
async def similarities_detector(sentences: list[str]):
    """
    Sentence Similarity Detection.

    Detect the similarity between a list of sentences.

    Parameters:
    - **sentences**: A list of sentences to compare for similarity.

    Returns:
    - **SentencesSimilarityResponse**: A response containing similarity scores for each sentence pair.

    Example Request:
    ```json
    POST /similarities-detector
    {
        "sentences": [
            "The quick brown fox jumps over the lazy dog.",
            "A fast fox jumps above the sleeping canine.",
            "Apples are red, and bananas are yellow."
        ]
    }
    ```

    Example Response:
    ```json
    {
        "data": [
            {"sentence": "A fast fox jumps above the sleeping canine.", "score": 0.78},
            {"sentence": "Apples are red, and bananas are yellow.", "score": 0.92}
        ]
    }
    ```
    """

    result = await processors.similarities_check(sentences)
    return SentencesSimilarityResponse(data=result)
