from transformers import pipeline


async def answer_question(doc, questions):
    pipe = pipeline("document-question-answering",
                    model="impira/layoutlm-document-qa")
    result = []
    for question in questions:
        result.append(pipe(doc, question))
    return result
