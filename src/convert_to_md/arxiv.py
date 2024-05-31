from pathlib import Path
from tempfile import TemporaryDirectory

from .models import ConversionTask, TaskStatus
from .util import download_file, run_command, unzip, zip_dir


def find_main_tex_file(directory: Path) -> Path:
    common_main_files = ["main.tex", "paper.tex", "ms.tex", "article.tex"]
    tex_files = list(directory.glob("*.tex"))
    for main_file in common_main_files:
        main_file_path = directory / main_file
        if main_file_path in tex_files:
            return main_file_path
    if tex_files:
        return tex_files[0]
    raise FileNotFoundError(f"No .tex files found in the directory '{directory}'.")


async def process_arxiv(
    context: str,
    original_file_path: Path,
    converted_file_path: Path,
    task: ConversionTask,
) -> None:
    try:
        await download_file(
            uri=f"https://arxiv.org/e-print/{context}",
            file_path=original_file_path,
        )
        convert_arxiv_paper(
            file_path=original_file_path,
            output_file_path=converted_file_path,
        )
        task.status = TaskStatus.completed
    except Exception as e:
        task.status = TaskStatus.failed
        task.error = str(e)


def convert_arxiv_paper(
    file_path: Path,
    output_file_path: Path,
) -> None:
    # Create a temporary directory for conversion
    with TemporaryDirectory() as temp_dir:
        unzip(
            input_file_path=str(file_path),
            output_dir=temp_dir,
        )

        temp_dir_path = Path(temp_dir)
        main_tex_file = find_main_tex_file(temp_dir_path)
        cvt_dir = temp_dir_path / "__cvt"
        cvt_dir.mkdir(exist_ok=True)

        run_command(
            f"latexml {main_tex_file} --destination={cvt_dir}/output.xml",
        )
        run_command(
            f"latexmlpost {cvt_dir}/output.xml --destination={cvt_dir}/output.html",
        )
        run_command(
            f"pandoc -f html -t markdown_strict {cvt_dir}/output.html -o {cvt_dir}/output.md",
        )

        zip_dir(
            input_dir=str(cvt_dir),
            output_file_path=str(output_file_path),
        )
