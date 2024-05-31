from pathlib import Path
from tempfile import TemporaryDirectory

from marker.convert import convert_single_pdf
from marker.logger import configure_logging
from marker.models import load_all_models
from marker.output import save_markdown

from .models import ConversionTask, TaskStatus
from .util import download_file, zip_dir

configure_logging()


async def process_pdf(
    context: str,
    original_file_path: Path,
    converted_file_path: Path,
    task: ConversionTask,
) -> None:
    try:
        await download_file(
            uri=context,
            file_path=original_file_path,
        )
        convert_pdf(
            file_path=original_file_path,
            output_file_path=converted_file_path,
        )
        task.status = TaskStatus.completed
    except Exception as e:
        task.status = TaskStatus.failed
        task.error = str(e)


def convert_pdf(
    file_path: Path,
    output_file_path: Path,
) -> None:
    model_lst = load_all_models()
    full_text, images, out_meta = convert_single_pdf(
        str(file_path),
        model_lst,
    )

    with TemporaryDirectory() as temp_dir:
        subfolder_path = save_markdown(
            temp_dir,
            file_path.name,
            full_text,
            images,
            out_meta,
        )
        print(f"Intermediate Markdown saved to {subfolder_path}")

        zip_dir(
            input_dir=temp_dir,
            output_file_path=str(output_file_path),
        )
