
import zipfile
from pathlib import Path
from app.core.config import settings
import httpx



def check_mineru_health() -> dict:
    response = httpx.get(
        f"{settings.mineru_api_url}/health",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def submit_mineru_task(
    file_path: Path,
    filename: str,
) -> dict:
    with file_path.open("rb") as file_handle:
        response = httpx.post(
            f"{settings.mineru_api_url}/tasks",
            files={
                "files": (
                    filename,
                    file_handle,
                    "application/pdf",
                )
            },
            data={
                "backend": "pipeline",
                "lang_list": "en",
                "parse_method": "auto",
                "formula_enable": "true",
                "table_enable": "true",
                "return_md": "true",
                "return_content_list": "true",
                "return_images": "false",
                "return_middle_json": "false",
                "return_model_output": "false",
                "response_format_zip": "true",
                "return_original_file": "false",
            },
            timeout=60,
        )

    response.raise_for_status()

    payload = response.json()

    if "task_id" not in payload:
        raise RuntimeError(
            "MinerU did not return a task_id."
        )

    return payload


def get_mineru_task(
    task_id: str,
) -> dict:
    response = httpx.get(
        f"{settings.mineru_api_url}/tasks/{task_id}",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def download_mineru_result(
    task_id: str,
    output_directory: Path,
) -> None:
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    response = httpx.get(
        (
            f"{settings.mineru_api_url}/tasks/"
            f"{task_id}/result"
        ),
        timeout=600,
    )

    response.raise_for_status()

    zip_path = (
        output_directory
        / "mineru_result.zip"
    )

    zip_path.write_bytes(
        response.content
    )

    with zipfile.ZipFile(
        zip_path,
        "r",
    ) as archive:
        root = (
            output_directory
            .resolve()
        )

        for member in archive.infolist():
            destination = (
                output_directory
                / member.filename
            ).resolve()

            if (
                destination != root
                and root
                not in destination.parents
            ):
                raise RuntimeError(
                    "Unsafe path in MinerU ZIP."
                )

        archive.extractall(
            output_directory
        )

    zip_path.unlink(
        missing_ok=True
    )