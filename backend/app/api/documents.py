from pathlib import Path
from datetime import date
from uuid import uuid4
from app.core.config import settings
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    BackgroundTasks,
)
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert
from app.db.session import get_db
from app.models.company import Company
from app.models.document import Document
from app.services.extraction.mineru_parser import (
    parse_financial_sections,
)
from app.services.extraction.deterministic_extractor import (
    extract_deterministic_metrics,
)
from app.services.extraction.validator import (
    validate_and_reconcile,
)
from app.models.extraction_candidate import (
    ExtractionCandidate,
)
from app.models.reported_metric import (
    ReportedMetric,
)
from app.models.reporting_period import (
    ReportingPeriod,
)
from app.services.extraction.mineru_processor import (
    process_document_with_mineru,
)
router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)

UPLOAD_DIRECTORY = Path(
    settings.upload_dir
)
UPLOAD_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


def get_mineru_directory(
    document_id: int,
) -> Path:
    return (
        UPLOAD_DIRECTORY
        / str(document_id)
        / "mineru"
    )

def create_reporting_period(
    company_id: int,
    code: str,
) -> ReportingPeriod:
    if code.startswith("FY"):
        year = int(
            code.replace("FY", "")
        )

        return ReportingPeriod(
            company_id=company_id,
            code=code,
            label=f"FY {year}",
            period_type="financial_year",
            start_date=date(
                year - 1,
                7,
                1,
            ),
            end_date=date(
                year,
                6,
                30,
            ),
        )

    if code.startswith("BS_"):
        _, year, month, day = code.split(
            "_"
        )

        snapshot_date = date(
            int(year),
            int(month),
            int(day),
        )

        return ReportingPeriod(
            company_id=company_id,
            code=code,
            label=(
                f"{snapshot_date.day} "
                f"{snapshot_date:%b %Y}"
            ),
            period_type="balance_sheet_snapshot",
            start_date=None,
            end_date=snapshot_date,
        )

    raise HTTPException(
        status_code=422,
        detail=(
            "Unsupported reporting period code: "
            f"{code}"
        ),
    )

def find_content_list(
    document_id: int,
) -> Path | None:
    mineru_directory = get_mineru_directory(
        document_id
    )

    if not mineru_directory.exists():
        return None

    patterns = [
        "*_content_list_v2.json",
    ]

    for pattern in patterns:
        matches = list(
            mineru_directory.rglob(
                pattern
            )
        )

        if matches:
            return matches[0]

    return None


def find_markdown(
    document_id: int,
) -> Path | None:
    mineru_directory = get_mineru_directory(
        document_id
    )

    if not mineru_directory.exists():
        return None

    matches = list(
        mineru_directory.rglob("*.md")
    )

    if not matches:
        return None

    return matches[0]


@router.post(
    "/upload",
    status_code=201,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    company = (
        db.query(Company)
        .filter(
            Company.name == "Senus PLC"
        )
        .first()
    )

    if company is None:
        company = Company(
            name="Senus PLC",
            ticker="SENUS",
            currency="EUR",
        )

        db.add(company)
        db.commit()
        db.refresh(company)

    original_name = (
        file.filename
        or "document.pdf"
    )

    stored_name = f"{uuid4()}.pdf"

    file_path = (
        UPLOAD_DIRECTORY
        / stored_name
    )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    file_path.write_bytes(contents)

    document = Document(
        company_id=company.id,
        name=original_name,
        document_type="financial_report",
        file_path=str(file_path),
        status="uploaded",
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    background_tasks.add_task(
    process_document_with_mineru,
    document.id,
)
    return {
        "id": document.id,
        "name": document.name,
        "status": document.status,
    }


@router.get("")
def get_documents(
    db: Session = Depends(get_db),
):
    documents = (
        db.query(Document)
        .order_by(Document.id.desc())
        .all()
    )

    return [
        {
            "id": document.id,
            "name": document.name,
            "document_type": (
                document.document_type
            ),
            "status": document.status,
            "created_at": document.created_at,
        }
        for document in documents
    ]


@router.get("/{document_id}/status")
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    content_list = find_content_list(
        document.id
    )

    return {
        "document_id": document.id,
        "name": document.name,
        "status": document.status,
        "mineru_task_id": (
            document.mineru_task_id
        ),
        "extraction_available": (
            content_list is not None
        ),
    }


@router.get("/{document_id}/content")
def get_document_content(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    markdown_path = find_markdown(
        document.id
    )

    if markdown_path is None:
        raise HTTPException(
            status_code=409,
            detail=(
                "MinerU Markdown output "
                "was not found."
            ),
        )

    markdown = markdown_path.read_text(
        encoding="utf-8"
    )

    return {
        "document_id": document.id,
        "content": markdown,
    }
@router.post(
    "/{document_id}/extract-metrics"
)
def extract_document_metrics(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    content_list = find_content_list(
        document.id
    )

    if content_list is None:
        raise HTTPException(
            status_code=409,
            detail=(
                "MinerU structured output "
                "was not found."
            ),
        )

    sections = parse_financial_sections(
        content_list
    )

    if not sections:
        raise HTTPException(
            status_code=422,
            detail=(
                "No supported financial "
                "statements were found."
            ),
        )

    raw_candidates = []

    for section in sections:
        print(
            f"Extracting "
            f"{section.statement_type}",
            flush=True,
        )

        result = (
            extract_deterministic_metrics(
                section
            )
        )

        print(
            f"{section.statement_type}: "
            f"{len(result.metrics)} candidates",
            flush=True,
        )

        raw_candidates.extend(
            result.metrics
        )

    metrics, validation = (
        validate_and_reconcile(
            raw_candidates
        )
    )

    period_codes = {
        metric.period_label
        for metric in metrics
    }

    periods = (
        db.query(ReportingPeriod)
        .filter(
            ReportingPeriod.company_id
            == document.company_id,
            ReportingPeriod.code.in_(
                period_codes
            ),
        )
        .all()
    )
    
    period_map = {
        period.code: period
        for period in periods
    }
    
    missing_periods = (
        period_codes
        - set(period_map.keys())
    )
    
    for code in sorted(missing_periods):
        period = create_reporting_period(
            company_id=document.company_id,
            code=code,
        )
    
        db.add(period)
        db.flush()
    
        period_map[code] = period

    try:
        db.query(
            ExtractionCandidate
        ).filter(
            ExtractionCandidate.document_id
            == document.id
        ).delete()

        saved_candidates = []

        for metric in metrics:
            candidate = (
                ExtractionCandidate(
                    company_id=(
                        document.company_id
                    ),
                    document_id=(
                        document.id
                    ),
                    period_code=(
                        metric.period_label
                    ),
                    metric_code=(
                        metric.metric_code
                    ),
                    value=metric.value,
                    currency=metric.currency,
                    unit=metric.unit,
                    statement_type=(
                        metric.statement_type
                    ),
                    source_page=(
                        metric.source_page
                    ),
                    source_text=(
                        metric.source_text
                    ),
                    confidence=(
                        metric.confidence
                    ),
                    validation_status=(
                        validation["status"]
                    ),
                )
            )

            db.add(candidate)

            saved_candidates.append(
                candidate
            )

        promoted = False

        if (
            validation["status"]
            == "validated"
        ):
            for metric in metrics:
                period = period_map[
                    metric.period_label
                ]
        
                stmt = insert(
                    ReportedMetric
                ).values(
                    company_id=document.company_id,
                    document_id=document.id,
                    period_id=period.id,
                    metric_code=metric.metric_code,
                    value=metric.value,
                    currency=metric.currency,
                    unit=metric.unit,
                    statement_type=metric.statement_type,
                    source_page=metric.source_page,
                    source_text=metric.source_text,
                    confidence=metric.confidence,
                    validation_status="validated",
                )
        
                stmt = stmt.on_conflict_do_update(
                    index_elements=[
                        "company_id",
                        "period_id",
                        "metric_code",
                    ],
                    set_={
                        "document_id": document.id,
                        "value": metric.value,
                        "currency": metric.currency,
                        "unit": metric.unit,
                        "statement_type": metric.statement_type,
                        "source_page": metric.source_page,
                        "source_text": metric.source_text,
                        "confidence": metric.confidence,
                        "validation_status": "validated",
                    },
                )
        
                db.execute(stmt)
        
            promoted = True

        db.commit()

        for candidate in (
            saved_candidates
        ):
            db.refresh(candidate)

    except Exception:
        db.rollback()
        raise

    return {
        "document_id": document.id,
        "raw_candidate_count": (
            len(raw_candidates)
        ),
        "metric_count": len(metrics),
        "validation": validation,
        "promoted_to_reported_metrics": (
            promoted
        ),
        "metrics": [
            {
                "metric_code": (
                    metric.metric_code
                ),
                "period_code": (
                    metric.period_label
                ),
                "value": metric.value,
                "currency": (
                    metric.currency
                ),
                "unit": metric.unit,
                "statement_type": (
                    metric.statement_type
                ),
                "source_page": (
                    metric.source_page
                ),
                "confidence": (
                    metric.confidence
                ),
            }
            for metric in metrics
        ],
    }

@router.get("/{document_id}/sections")
def get_document_sections(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    content_list = find_content_list(
        document.id
    )

    if content_list is None:
        raise HTTPException(
            status_code=409,
            detail=(
                "MinerU structured output "
                "was not found."
            ),
        )

    sections = parse_financial_sections(
        content_list
    )

    return {
        "document_id": document.id,
        "sections": [
            section.model_dump()
            for section in sections
        ],
    }