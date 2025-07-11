from langchain.llms import Ollama


def compare_documents(doc1, doc2, prompt=None):
    llm = Ollama(model="mistral")

    if prompt:
        full_prompt = f"""Compare the two documents below based on the user's request.\n\n
        Document A:\n{doc1}\n\n
        Document B:\n{doc2}\n\n
        User Query: {prompt}\n\n
        Provide the comparison in a structured Markdown table."""
    else:
        full_prompt = f"""Compare the following two documents and highlight differences and similarities in a Markdown table format.

        Document A:\n{doc1}\n\n
        Document B:\n{doc2}"""

    response = llm.invoke(full_prompt)
    return response
