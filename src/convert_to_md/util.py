import hashlib
import os
import subprocess
import tarfile
from pathlib import Path

import aiohttp
from fastapi import HTTPException


def run_command(command) -> None:
    process = subprocess.Popen(command, shell=True)
    process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed: {command}")


async def download_file(uri: str, file_path: Path) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(uri) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status, detail="Failed to download file"
                )
            content = await response.read()
            with open(file_path, "wb") as f:
                f.write(content)


def mk_zip_filename(id: str) -> str:
    file_name = (
        hashlib.md5(
            id.encode(),
        ).hexdigest()
        + ".tar.gz"
    )

    return file_name


def unzip(
    input_file_path: str,
    output_dir: str,
) -> None:
    with tarfile.open(input_file_path, "r:gz") as tar:
        tar.extractall(path=output_dir)


def zip_dir(
    input_dir: str,
    output_file_path: str,
) -> None:
    with tarfile.open(output_file_path, "w:gz") as tar:
        tar.add(input_dir, arcname=os.path.basename(input_dir))
