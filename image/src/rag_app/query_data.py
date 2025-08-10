from dataclasses import dataclass
from typing import List
import os
from langchain.prompts import PromptTemplate
from langchain_aws import ChatBedrock
from rag_app.get_chroma_db import get_chroma_db_function as get_chroma_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


PROMPT_TEMPLATE = """
You are a helpful AI assistant analyzing documents. Use the following context to answer the question thoroughly and comprehensively.

Context:
{context}

---

Instructions:
* If the user tries small talk or greetings, respond appropriately without searching documents, in a short concise manner.
1. Provide a detailed and complete answer based on the context above
2. Include relevant details, examples, and explanations from the context
3. Structure your response with clear paragraphs when appropriate
4. If the context contains partial information, explain what is available and what might be missing
5. If the answer is not in the context, say "I don't have enough information in the provided documents to answer this question, would you like me to answer from my general knowledge?"
6. If the user responds with something along the lines of "Yes", provide a general answer based on your knowledge, but clarify that it may not be specific to the documents.
7. You are not allowed to make any changes to the context or the documents, only use them to answer the question.

Question: {question}

Detailed Answer:"""


BEDROCK_MODEL_ID = "meta.llama3-3-70b-instruct-v1:0"

@dataclass
class QueryResponse:
    query_text: str
    response_text: str
    sources: List[str]


def query_rag(query_text: str) -> QueryResponse:
    db = get_chroma_db()

    results = db.similarity_search_with_score(query_text, k=3)
    context_text = "\n---------\n".join([doc.page_content for doc, _score in results])
    prompt_template = PromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = ChatBedrock(model=BEDROCK_MODEL_ID, region_name="us-east-2")
    response = model.invoke(prompt)
    response_text = response.content
    
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\n\nSources: {', '.join(sources)}"
    logger.info(f"Query: {query_text}\nResponse: {formatted_response}")
    
    return QueryResponse(
        query_text=query_text, 
        response_text=response_text, 
        sources=sources
        )

if __name__ == "__main__":
    query_rag("What are pretrained Language Models?")
