"""
Extended service to convert different types of documents to markdown:

1. Handling PDF download and storage.
2. Handling arXiv paper download and conversion.
3. Converting the documents.
4. Allowing clients to poll the status of the conversion.
5. Handling caching and conversion status.
"""

import logging
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse

from .arxiv import process_arxiv
from .models import (
    ArXivRequest,
    ConversionRequest,
    ConversionTask,
    PDFRequest,
    TaskStatus,
)
from .pdf import process_pdf
from .util import mk_zip_filename

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.debug("This is a debug message.")

app = FastAPI()

# Directories for storing files
ORIGINAL_DIR = Path("./original_files")
CONVERTED_DIR = Path("./converted_files")
ORIGINAL_DIR.mkdir(parents=True, exist_ok=True)
CONVERTED_DIR.mkdir(parents=True, exist_ok=True)

conversion_tasks: dict[str, ConversionTask] = {}


@app.post("/convert")
async def convert_request(
    request: ConversionRequest,
    background_tasks: BackgroundTasks,
) -> ConversionTask:
    if request.type == "pdf":
        pdf_request: PDFRequest = PDFRequest.model_validate(request.data)
        request_id = pdf_request.uri
        process_fn = process_pdf
    elif request.type == "arxiv":
        arxiv_request: ArXivRequest = ArXivRequest.model_validate(request.data)
        request_id = arxiv_request.arxiv_id
        process_fn = process_arxiv
    else:
        raise HTTPException(status_code=400, detail="Unknown conversion type")

    file_name = mk_zip_filename(request_id)
    original_file_path = ORIGINAL_DIR / file_name
    converted_file_path = CONVERTED_DIR / file_name

    if converted_file_path.exists():
        return ConversionTask(
            status=TaskStatus.completed,
            file_name=file_name,
        )

    task_id = str(uuid.uuid4())
    task = ConversionTask(
        task_id=task_id,
        file_name=file_name,
    )
    conversion_tasks[task_id] = task

    background_tasks.add_task(
        process_fn,
        request_id,
        original_file_path,
        converted_file_path,
        task,
    )

    return task


@app.get("/status/{task_id}")
async def get_conversion_status(task_id: str) -> ConversionTask:
    if task_id not in conversion_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return conversion_tasks[task_id]


@app.get("/download/{file_name}")
async def download_file_route(file_name: str) -> FileResponse:
    converted_file_path = CONVERTED_DIR / file_name
    if not converted_file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=converted_file_path)
