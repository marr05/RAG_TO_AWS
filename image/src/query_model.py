import os
import time
import uuid
import boto3
from pydantic import BaseModel, Field
from typing import List, Optional
from botocore.exceptions import ClientError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TABLE_NAME = os.environ.get("TABLE_NAME")


class QueryModel(BaseModel):
    query_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    created_time: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    query_text: str
    answer_text: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
    is_complete: bool = False

    @classmethod
    def get_table(cls: "QueryModel") -> boto3.resource:
        dynamodb = boto3.resource("dynamodb")
        return dynamodb.Table(TABLE_NAME)

    def put_item(self):
        item = self.as_ddb_item()
        try:
            QueryModel.get_table().put_item(Item=item)
        except ClientError as e:
            logger.info(f"ClientError, {e.response["Error"]["Message"]}")
            raise e

    def as_ddb_item(self):
        item = {k: v for k, v in self.dict().items() if v is not None}
        return item

    @classmethod
    def get_item(cls: "QueryModel", query_id: str) -> "QueryModel":
        try:
            response = cls.get_table().get_item(Key={"query_id": query_id})
        except ClientError as e:
            logger.info(f"ClientError, {e.response["Error"]["Message"]}")
            return None

        if "Item" in response:
            item = response["Item"]
            return cls(**item)
        else:
            return None