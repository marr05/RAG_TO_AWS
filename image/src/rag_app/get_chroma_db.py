from langchain_chroma import Chroma
from rag_app.get_embeddings import get_embedding_function

import os
import sys
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


CHROMA_PATH = os.path.join(os.getcwd(), "data/chroma_db")
IS_USING_IMAGE_RUNTIME = bool(os.environ.get("IS_USING_IMAGE_RUNTIME", False))
CHROMA_DB_INSTANCE = None # Reference to a single instance of Chroma DB

def get_chroma_db_function():
    global CHROMA_DB_INSTANCE
    if not CHROMA_DB_INSTANCE:

        # Hack needed for AWS Lambda's base Python Image (to work with an updated version of SQLite)
        # In lambda runtime, we need to copy ChromaDB to /tmp so it can have write permissions
        if IS_USING_IMAGE_RUNTIME:
            __import__("pysqlite3")
            sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
            copy_chroma_to_tmp()
            
        # Prepare DB
        CHROMA_DB_INSTANCE = Chroma(
            persist_directory=get_runtime_chroma_path(),
            embedding_function=get_embedding_function()
        )
        logger.info(f"Chroma DB instance {CHROMA_DB_INSTANCE} initialized at {get_runtime_chroma_path()}")
    
    return CHROMA_DB_INSTANCE


def copy_chroma_to_tmp():
    '''
    Checks if a temp path exists, if not, it creates a new path and copies the Chroma DB from the original path to the runtime temp path.
    '''
    dst_chroma_path = get_runtime_chroma_path()
    
    if not os.path.exists(dst_chroma_path):
        os.makedirs(dst_chroma_path)
        
    tmp_contents = os.listdir(dst_chroma_path)
    if len(tmp_contents) == 0:
        logger.info(f"Copying Chroma DB from {CHROMA_PATH} to {dst_chroma_path}")
        os.makedirs(dst_chroma_path, exist_ok=True)
        shutil.copytree(CHROMA_PATH, dst_chroma_path, dirs_exist_ok=True)
        
    else:
        logger.info(f"Chroma DB already exists at {dst_chroma_path}, skipping copy.")
        
        
#We add a fxn to get the where the chroma db is running in during runtime, locally or in AWS.
def get_runtime_chroma_path():
    if IS_USING_IMAGE_RUNTIME:
        return f"/tmp/{CHROMA_PATH}"
    else:
        return CHROMA_PATH