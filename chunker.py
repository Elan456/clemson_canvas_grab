"""
Converts the files to chunks and saves them in a jsonl file

i.e.

{"doc_id": "12545", "doc_name": "file1", "doc_text": "This is the text in file1 up to max_chunk_size characters"}

Save in the BEIR format 
"""

import json 
import os 
from langchain.text_splitter import RecursiveCharacterTextSplitter

MAX_CHUNK_SIZE = 1000

def chunk_with_langchain(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=MAX_CHUNK_SIZE, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    return chunks

def corpus_generator(folder_path, output_path):
    """
    Will grab every json file in the folder_path and combine them into a single json file with each chunk with an ID
    """

    corpus = {}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.split(".")[-1] != "json":
                continue

            if file == "corpus.json":
                continue

            file_path = os.path.join(root, file)
            with open(file_path, "r") as f:
                data = json.load(f)


            source_document_name = data["document_name"]
            content = data["content"]

            # Handling the PDF per page style
            if type(content) == list:
                c = ""
                for section in content:
                    page_number = section.get("page_number", "")
                    paragraph_number = section.get("paragraph_number", "")
                    
                    if page_number:
                        c += f"Page {page_number}\n"
                    if paragraph_number:
                        c += f"Paragraph {paragraph_number}\n"

                    c += section["text"]
                content = c
                
            chunks = chunk_with_langchain(content)

            for idx, chunk in enumerate(chunks):
                chunk_id = len(corpus)
                corpus[chunk_id] = {
                    "title": f"{source_document_name} - {idx}",
                    "text": chunk,
                    "metadata": {
                        "source_document_name": source_document_name,
                        "sequence_number": idx
                    }
                }
    # Save the corpus
    corpus_path = os.path.join(output_path, "corpus.json")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with open(corpus_path, "w") as f:
        json.dump(corpus, f, indent=4)
        print(f"Saved corpus to {corpus_path}")




if __name__ == "__main__":
    corpus_generator("../grabbing_test/S2408-CPSC-1900 Teaching Assist Fundamentals - 002 - 90288", "corpus_test")