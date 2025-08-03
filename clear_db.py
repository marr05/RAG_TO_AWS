# python script to clear the chroma database
import os
from langchain_chroma import Chroma
import shutil

CHROMA_PATH = os.getenv("CHROMA_PATH")

def clear_chroma_db():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print(f"Cleared the Chroma database at {CHROMA_PATH}")
    else:
        print("No existing Chroma database to clear.")
        
if __name__ == "__main__":
    clear_chroma_db()
