import uvicorn
import json
import boto3
from typing import Optional
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel
from query_model import QueryModel
from rag_app.query_data import query_rag
import os 
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WORKER_LAMBDA_NAME = os.environ.get("WORKER_LAMBDA_NAME", None)
CHARACTER_LIMIT = 2000

app = FastAPI()
handler = Mangum(app)  # Entry point for AWS Lambda.

class SubmitQueryRequest(BaseModel):
    query_text: str
    user_id : Optional[str] = None  # Optional user ID

@app.get("/")
def index():
    return {"Hello": "World"}

@app.get("/get_query")
def get_query_endpoint(query_id:str) -> QueryModel:
    query = QueryModel.get_item(query_id)
    # return query
    if query:
        return query
    else:
        raise HTTPException(status_code=404, detail="Query not found: {query_id}")
    
@app.get("/list_query")
def list_query_endpoint(user_id: str) -> list[QueryModel]:
    ITEM_COUNT = 25
    logger.info(f"Listing queries for user: {user_id}")
    query_items = QueryModel.list_items(user_id=user_id, count=ITEM_COUNT)
    return query_items

@app.post("/submit_query")
def submit_query_endpoint(request: SubmitQueryRequest) -> QueryModel:
    
    if len(request.query_text) > CHARACTER_LIMIT:
        raise HTTPException (
            status_code=400, 
            detail=f"Query text exceeds {CHARACTER_LIMIT} characters limit."
        )
    
    user_id = request.user_id if request.user_id else "anonymous"
    query = QueryModel(query_text=request.query_text, user_id=user_id)
    
    if WORKER_LAMBDA_NAME:
        # Make asynchronous call to worker lambda
        query.put_item()  # Save initial query to DB
        invoke_worker(query)
    else:
        # Make synchronous call to RAG if no worker lambda is defined
        query_response = query_rag(request.query_text)
        query.answer_text = query_response.response_text
        query.sources = query_response.sources
        query.is_complete = True
        query.put_item()  # Save completed query to DB
        
    return query

    
def invoke_worker(query: QueryModel):
    # initialize boto3 lambda client
    lambda_client = boto3.client("lambda")
    
    # Getting the QueryModel as a dictionary to send to the worker lambda
    payload = query.model_dump()
    
    # Invoke another lambda function asynchronously
    response = lambda_client.invoke(
        FunctionName=WORKER_LAMBDA_NAME,
        InvocationType="Event",  # Asynchronous invocation
        Payload=json.dumps(payload),
    )
    
    logger.info(f"Invoked worker lambda {WORKER_LAMBDA_NAME} for query_id {query.query_id} with response: {response}")
    return response

if __name__ == "__main__":
    # Run this as a server directly.
    port = 3000
    logger.info(f"Running the FastAPI server on port {port}.")
    uvicorn.run("app_api_handler:app", host="0.0.0.0", port=port)