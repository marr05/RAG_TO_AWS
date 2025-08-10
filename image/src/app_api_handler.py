import uvicorn
from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel
from query_model import QueryModel
from rag_app.query_data import QueryResponse, query_rag
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
handler = Mangum(app)  # Entry point for AWS Lambda.

class SubmitQueryRequest(BaseModel):
    query_text: str

@app.get("/")
def index():
    return {"Hello": "World"}

@app.get("/get_query")
def get_query_endpoint(query_id:str) -> QueryModel:
    query = QueryModel.get_item(query_id)
    return query

@app.post("/submit_query")
def submit_query_endpoint(request: SubmitQueryRequest) -> QueryModel:
    query_response = query_rag(request.query_text)
    
    # Creating query item and putting into db
    new_query = QueryModel(
        query_text=request.query_text,
        answer_text=query_response.response_text,
        sources=query_response.sources,
        is_complete=True
    )
    new_query.put_item()
    return new_query

if __name__ == "__main__":
    # Run this as a server directly.
    port = 3000
    logger.info(f"Running the FastAPI server on port {port}.")
    uvicorn.run("app_api_handler:app", host="0.0.0.0", port=port)