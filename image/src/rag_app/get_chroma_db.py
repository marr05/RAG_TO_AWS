from langchain_chroma import Chroma
import os
from rag_app.get_embeddings import get_embedding_function as get_embeddings
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH")
CHROMA_DB_INSTANCE = None

def get_chroma_db_function():
    global CHROMA_DB_INSTANCE
    if not CHROMA_DB_INSTANCE:
        # Prepare DB
        CHROMA_DB_INSTANCE = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=get_embeddings()
        )
        print(f"Chroma DB instance {CHROMA_DB_INSTANCE} initialized at {CHROMA_PATH}")
    return CHROMA_DB_INSTANCE