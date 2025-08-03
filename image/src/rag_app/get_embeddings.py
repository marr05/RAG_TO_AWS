from langchain_aws import BedrockEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

def get_embedding_function():
    embeddings = BedrockEmbeddings(
        model_id=os.getenv("AMZ_TITAN_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0"),
        region_name="us-east-2"
    )
    return embeddings 