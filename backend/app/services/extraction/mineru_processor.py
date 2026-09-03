import time
from pathlib import Path
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.document import Document
from app.services.extraction.mineru_client import (
    download_mineru_result,
    get_mineru_task,
    submit_mineru_task,
)


UPLOAD_DIRECTORY = Path(
    settings.upload_dir
)


def process_document_with_mineru(
    document_id: int,
) -> None:
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(
                Document.id
                == document_id
            )
            .first()
        )

        if document is None:
            return

        file_path = Path(
            document.file_path
        )

        if not file_path.exists():
            document.status = "failed"
            db.commit()
            return

        task = submit_mineru_task(
            file_path=file_path,
            filename=document.name,
        )

        task_id = task["task_id"]

        document.mineru_task_id = (
            task_id
        )
        document.status = "pending"

        db.commit()

        while True:
            task_status = (
                get_mineru_task(
                    task_id
                )
            )

            status = task_status.get(
                "status"
            )

            if status in {
                "pending",
                "processing",
            }:
                document.status = status
                db.commit()

                time.sleep(2)

                continue

            if status == "failed":
                document.status = "failed"
                db.commit()

                return

            if status == "completed":
                break

            document.status = "failed"
            db.commit()

            return

        output_directory = (
            UPLOAD_DIRECTORY
            / str(document.id)
            / "mineru"
        )

        download_mineru_result(
            task_id=task_id,
            output_directory=(
                output_directory
            ),
        )

        document.status = "processed"

        db.commit()

    except Exception as exc:
        print(
            f"MinerU processing failed "
            f"for document {document_id}: "
            f"{exc}",
            flush=True,
        )

        document = (
            db.query(Document)
            .filter(
                Document.id
                == document_id
            )
            .first()
        )

        if document is not None:
            document.status = "failed"
            db.commit()

    finally:
        db.close()