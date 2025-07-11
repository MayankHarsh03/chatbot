from langchain.llms import Ollama
from langchain.chains.question_answering import load_qa_chain


def ask_question(vector_db, query):
    llm = Ollama(model="mistral")

    if vector_db:
        retriever = vector_db.as_retriever()
        chain = load_qa_chain(llm, chain_type="stuff")
        docs = retriever.get_relevant_documents(query)
        answer = chain.run(input_documents=docs, question=query)
        return answer
    else:
        # No vector DB — just use plain LLM response
        response = llm.invoke(query)
        return response
