import argparse
import os
import shutil
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain_community.vectorstores import Chroma
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal
import threading

stop_event = threading.Event()


def signal_handler(signum, frame):
    print("\nInterrupt signal received! Stopping...")
    stop_event.set()


signal.signal(signal.SIGINT, signal_handler)


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
    print("Loading files...")
    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".json"):
            file_path = os.path.join(DATA_PATH, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    print(
                        f"Loading json file: {file_path} with {
                            len(data.keys())} entries..."
                    )
                    for key, value in data.items():
                        metadata = {"source": filename, "current_key": key}
                        documents.append(Document(
                            page_content=json.dumps({key: value}),
                            metadata=metadata
                        ))
    return documents


def split_documents(documents: list[Document]):
    print("Splitting data into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    splits = text_splitter.split_documents(documents)
    print("Chunksplitting done...")
    return splits


def add_to_chroma(chunks: List[Document]):
    print("Initializing chroma with embedding function...")
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )
    print("Calculating chunk ids...")
    chunks_with_ids = calculate_chunk_ids(chunks)
    print("Checking already stored chunks...")
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Number of stored chunks: {len(existing_ids)}")
    new_chunks = [
        chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids
    ]

    total_chunks = len(new_chunks)
    print(f"New chunks: {total_chunks}")
    if not new_chunks:
        print("No new chunks...")
        return

    def process_chunk(chunk):
        chunk_id = chunk.metadata["id"]
        try:
            db.add_documents([chunk], ids=[chunk_id])
            print(f"{chunk_id} stored...")
        except Exception as e:
            print(f"Storing failed: {e}")

    completed_chunks = 0
    try:
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(
                process_chunk, chunk): chunk for chunk in new_chunks}
            for future in as_completed(futures):
                if stop_event.is_set():
                    print("Interrupt detected. Cancelling remaining tasks...")
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                try:
                    future.result()
                    completed_chunks += 1
                    progress = (completed_chunks / total_chunks) * 100

                    print(
                        f"Processed chunk: {
                            completed_chunks - 1} ({completed_chunks}/{total_chunks}, {progress:.2f}% complete)"
                    )
                except Exception as e:
                    print(f"Task failed: {e}")

    except KeyboardInterrupt:
        print("Forcefully stopping...")
    finally:
        if stop_event.is_set():
            print("Cleanup complete. Exiting.")


def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        key = chunk.metadata.get("current_key")
        current_page_id = f"{source}:{key}"

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
