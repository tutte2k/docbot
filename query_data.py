from langchain_community.vectorstores import Chroma

from langchain.prompts import ChatPromptTemplate
from get_embedding_function import get_embedding_function


CHROMA_PATH = "chroma"


def generate_template():

    def instructs(x, y):
        threat = "Bad answers gets severely punished and good answers gets rewarded."
        instr = f"""Answer the question only based on the {x} information{y}"""

        if (x == 'above'):
            instr = instr+threat
        else:
            instr = threat+instr

        return instr

    prep = f"""{
        instructs('following', ':')
    }\n---\n<!#!#!#>\n---\n{
        instructs('above', '!!!').upper()
    }\n<#!#!#!>???????????"""

    template = prep.replace("<!#!#!#>", "{context}").replace(
        "<#!#!#!>", "{question}"
    )

    return template


PROMPT_TEMPLATE = generate_template()


def query_rag(model, query_text: str):
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH,
                embedding_function=embedding_function)

    results = db.similarity_search_with_score(query_text, k=5)
    context_text = "\n\n---\n\n".join(
        [doc.page_content for doc, _ in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    sources = [doc.metadata["id"] for doc, _ in results]
    return (model.stream(prompt), sources)
