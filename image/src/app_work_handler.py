from query_model import QueryModel
from rag_app.query_data import QueryResponse, query_rag
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# invoked directly by the app_api_handler.py
# event object is a dictionary
def handler(event, context):
    query_item = QueryModel( **event) # here event is getting exploded, and the QueryModel objects info is being stored in query_item in strucured format
    invoke_rag(query_item)  # this will call the query_rag function to get the response from RAG
    
def invoke_rag(query_item: QueryModel):
    rag_response = query_rag(query_item.query_text)
    # now we update the query_item with the response from RAG 
    # since we want to store the response in the database, we update the query_item's attributes
    query_item.answer_text = rag_response.response_text
    query_item.sources = rag_response.sources
    query_item.is_complete = True
    query_item.put_item()  # save the updated query item to the database
    logger.info(f"Query {query_item.query_id} processed successfully with response: {query_item.answer_text}")
    return query_item