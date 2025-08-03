import uvicorn
from mangum import Mangum
from fastapi import FastAPI
from pydantic import BaseModel
from rag_app.query_data import QueryResponse, query_rag

app = FastAPI()
handler = Mangum(app)

class SubmitQueryRequest(BaseModel):
    query_text: str

@app.get("/")
def index():
    return {"message": "Welcome to the RAG-TO-AWS API!"}

@app.post("/submit_query")
def submit_query_endpoint(request: SubmitQueryRequest) -> QueryResponse:
    response = query_rag(request.query_text)
    return response


if __name__ == "__main__":
    port = 3000
    print(f"Running FastAPI on port {port}...")
    uvicorn.run("app_api_handler:app", host="0.0.0.0", port=port, reload=True)
