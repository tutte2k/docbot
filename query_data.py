from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain.prompts import ChatPromptTemplate
from get_embedding_function import get_embedding_function
from langchain_community.llms.ollama import Ollama

"""
1. create env:
python -m venv rag
2. activate env:
./rag/scripts/activate
3. install requirements:
pip install -r requirements.txt


to populate db with json content from data folder:
python populate_database.py     [--reset] to reset contents before populating
"""

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def query_rag(model, query_text: str):
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH,
                embedding_function=embedding_function)

    results = db.similarity_search_with_score(query_text, k=5)
    context_text = "\n\n---\n\n".join(
        [doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    sources = [doc.metadata["id"] for doc, _ in results]
    return (model.stream(prompt), sources)


def get_embedding_function():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings
