from transformers import pipeline


async def answer_question(doc, questions):
    pipe = pipeline("document-question-answering",
                    model="impira/layoutlm-document-qa")
    result = []
    for question in questions:
        out = pipe(doc, question)
        if not out:
            continue
        out[0]["question"] = question
        result.append(out[0])
    return result
