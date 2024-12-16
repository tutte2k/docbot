import argparse
import os
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_community.vectorstores import Chroma
import json


CHROMA_PATH = "chroma"
DATA_PATH = "data"


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true",
                        help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("Clearing Database")
        clear_database()

    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)


def load_documents():
    documents = []
    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".json"):  # Only process JSON files
            file_path = os.path.join(DATA_PATH, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                # Handle each file's data
                if isinstance(data, list):  # If JSON is an array
                    for item in data:
                        documents.append(Document(page_content=json.dumps(
                            item), metadata={"source": filename}))
                else:  # If JSON is a single object
                    documents.append(Document(page_content=json.dumps(
                        data), metadata={"source": filename}))
    return documents


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    chunks_with_ids = calculate_chunk_ids(chunks)

    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            print(chunk.metadata["id"])
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"New documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        for i, (chunk, chunk_id) in enumerate(zip(new_chunks, new_chunk_ids), 1):
            db.add_documents([chunk], ids=[chunk_id])
            print(f"""{i}/{len(new_chunks)} - Processed document:{
                  chunk.metadata["id"]}""")
    else:
        print("No new documents to add")


def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


if __name__ == "__main__":
    main()
