from enum import StrEnum
from typing import Union

from pydantic import BaseModel


class PDFRequest(BaseModel):
    uri: str


class ArXivRequest(BaseModel):
    arxiv_id: str


class ConversionRequest(BaseModel):
    type: str  # 'pdf' or 'arxiv'
    data: Union[PDFRequest, ArXivRequest]


class TaskStatus(StrEnum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class ConversionTask(BaseModel):
    status: str = TaskStatus.pending
    task_id: str | None = None
    file_name: str | None = None
    error: str | None = None
