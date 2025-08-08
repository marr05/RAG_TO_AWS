import argparse
import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from src.rag_app.get_embeddings import get_embedding_function
from langchain.schema.document import Document

CHROMA_PATH = "src/data/chroma_db"
DATA_PATH = "src/data"

def load_data(data_path):
    """Load data from the specified path."""
    loader = PyPDFDirectoryLoader(data_path)
    return loader.load()

def split_documents(documents):
    """Split documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120,
        length_function=len,
        is_separator_regex=False,
    )
    split_docs = text_splitter.split_documents(documents)
    return split_docs


def add_to_chroma_db(chunks: list[Document]):
    """Main function to add documents to the Chroma database."""
    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function(),
    )
    
    # calculating page ids
    chunks_with_ids = calculate_chunk_ids(chunks)

    #for chunk in chunks:
    #    print(f"chunk Page Sample: {chunk.metadata['id']}\n{chunk.page_content}\n\n")
        

    # add or update documents
    existing_items = vector_store.get(include=[])    # IDs are included by default
    existing_ids = set(existing_items['ids'])
    print(f"Existing IDs in the database: {len(existing_ids)}")
    
    # Only adding new documents
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata['id'] not in existing_ids:
            new_chunks.append(chunk)
            
    if len(new_chunks):
        print(f"Adding new documents : {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata['id'] for chunk in new_chunks]
        vector_store.add_documents(new_chunks, ids = new_chunk_ids)   
    else:
        print("No new documents to add.")
    
def calculate_chunk_ids(chunks):
    # Example id: "data/book.pdf:6:2"
    # Page source : Page Number : Chunk Index 
    
    last_page_id = None
    current_chunk_index = 0
    
    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"
        
        # if page id is the same as the last one, increment the chunk index
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0
            
        # calculate chunk id
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        
        # Add it to page metadata
        chunk.metadata['id'] = chunk_id
        
    return chunks

def clear_database():
    """Clear the Chroma database."""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print(f"Cleared the database at {CHROMA_PATH}")
    else:
        print("No existing database to clear.")
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database before populating it.")
    args = parser.parse_args()
    if args.reset:
        print("Clearing the database...")
        clear_database()

    # Creating (or updating) the Chroma database
    documents = load_data(DATA_PATH)
    chunks = split_documents(documents)
    add_to_chroma_db(chunks)
    
if __name__ == "__main__":
    main()
    