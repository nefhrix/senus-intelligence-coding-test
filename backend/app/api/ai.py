from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document
from app.models.extraction_candidate import (
    ExtractionCandidate,
)
from app.models.reporting_period import ReportingPeriod
from app.models.reported_metric import ReportedMetric

from app.services.ai.board_insights import (
    generate_board_insights,
    match_cited_sources,
)

from app.services.financials.calculations import (
    cash_ratio,
    current_ratio,
    ebitda,
    ebitda_margin,
    free_cash_flow,
    gross_margin,
    growth_rate,
    operating_margin,
    revenue_per_employee,
    working_capital,
)


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
)


class BoardInsightsRequest(BaseModel):
    question: str | None = None


def load_metrics(
    db: Session,
    period_id: int,
) -> dict[str, float]:
    rows = (
        db.query(ReportedMetric)
        .filter(
            ReportedMetric.period_id
            == period_id
        )
        .all()
    )

    return {
        row.metric_code: row.value
        for row in rows
    }


def load_metrics_with_sources(
    db: Session,
    period_id: int,
    period_code: str,
) -> tuple[dict[str, float], list[dict]]:


    rows = (
        db.query(ReportedMetric, Document)
        .join(
            Document,
            ReportedMetric.document_id == Document.id,
        )
        .filter(
            ReportedMetric.period_id == period_id
        )
        .all()
    )

    values = {
        metric.metric_code: metric.value
        for metric, _ in rows
    }

    lookup = [
        {
            "period_code": period_code,
            "metric_code": metric.metric_code,
            "value": metric.value,
            "source_page": metric.source_page,
            "document_id": metric.document_id,
            "document_name": document.name,
        }
        for metric, document in rows
    ]

    return values, lookup


def find_unvalidated_pending_documents(
    db: Session,
) -> list[dict]:


    rows = (
        db.query(Document)
        .join(
            ExtractionCandidate,
            ExtractionCandidate.document_id == Document.id,
        )
        .filter(
            ExtractionCandidate.validation_status
            == "needs_review"
        )
        .distinct()
        .all()
    )

    return [
        {
            "document_id": document.id,
            "name": document.name,
            "uploaded_at": str(document.created_at),
        }
        for document in rows
    ]


def get_period(
    db: Session,
    code: str,
) -> ReportingPeriod:
    period = (
        db.query(ReportingPeriod)
        .filter(
            ReportingPeriod.code
            == code
        )
        .first()
    )

    if period is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Reporting period "
                f"{code} not found"
            ),
        )

    return period


def build_financial_year_context(
    metrics: dict[str, float],
    previous_metrics: dict[str, float] | None = None,
) -> dict:
    previous_metrics = (
        previous_metrics or {}
    )

    return {
        "reported_metrics": metrics,
        "derived_metrics": {
            "revenue_growth": growth_rate(
                metrics.get("revenue"),
                previous_metrics.get(
                    "revenue"
                ),
            ),
            "gross_margin": gross_margin(
                metrics
            ),
            "operating_margin": operating_margin(
                metrics
            ),
            "ebitda": ebitda(
                metrics
            ),
            "ebitda_margin": ebitda_margin(
                metrics
            ),
            "free_cash_flow": free_cash_flow(
                metrics
            ),
            "working_capital": working_capital(
                metrics
            ),
            "current_ratio": current_ratio(
                metrics
            ),
            "cash_ratio": cash_ratio(
                metrics
            ),
            "revenue_per_employee": revenue_per_employee(
                metrics
            ),
        },
    }


def build_snapshot_context(
    metrics: dict[str, float],
) -> dict:
    return {
        "reported_metrics": metrics,
        "derived_metrics": {
            "working_capital": working_capital(
                metrics
            ),
            "current_ratio": current_ratio(
                metrics
            ),
            "cash_ratio": cash_ratio(
                metrics
            ),
        },
    }


@router.post("/board-insights")
def create_board_insights(
    request: BoardInsightsRequest,
    db: Session = Depends(get_db),
):
    fy2024 = get_period(
        db,
        "FY2024",
    )

    fy2025 = get_period(
        db,
        "FY2025",
    )

    snapshot = get_period(
        db,
        "BS_2025_12_08",
    )

    fy2024_metrics, fy2024_sources = (
        load_metrics_with_sources(
            db, fy2024.id, "FY2024"
        )
    )

    fy2025_metrics, fy2025_sources = (
        load_metrics_with_sources(
            db, fy2025.id, "FY2025"
        )
    )

    snapshot_metrics, snapshot_sources = (
        load_metrics_with_sources(
            db, snapshot.id, snapshot.code
        )
    )

    metric_lookup = (
        fy2024_sources
        + fy2025_sources
        + snapshot_sources
    )

    unvalidated_pending_documents = (
        find_unvalidated_pending_documents(db)
    )

    financial_context = {
        "as_of_date": str(date.today()),

        "unvalidated_pending_documents": (
            unvalidated_pending_documents
        ),

        "company": {
            "name": "Senus",
            "currency": "EUR",
        },

        "reporting_periods": {
            "FY2024": {
                "period_code": (
                    fy2024.code
                ),
                "period_label": (
                    fy2024.label
                ),
                "period_type": (
                    fy2024.period_type
                ),
                "start_date": (
                    str(
                        fy2024.start_date
                    )
                    if fy2024.start_date
                    else None
                ),
                "end_date": str(
                    fy2024.end_date
                ),
            },

            "FY2025": {
                "period_code": (
                    fy2025.code
                ),
                "period_label": (
                    fy2025.label
                ),
                "period_type": (
                    fy2025.period_type
                ),
                "start_date": (
                    str(
                        fy2025.start_date
                    )
                    if fy2025.start_date
                    else None
                ),
                "end_date": str(
                    fy2025.end_date
                ),
            },

            "latest_balance_sheet_snapshot": {
                "period_code": (
                    snapshot.code
                ),
                "period_label": (
                    snapshot.label
                ),
                "period_type": (
                    snapshot.period_type
                ),
                "date": str(
                    snapshot.end_date
                ),
            },
        },

        "FY2024": {
            **build_financial_year_context(
                fy2024_metrics
            ),
        },

        "FY2025": {
            **build_financial_year_context(
                fy2025_metrics,
                fy2024_metrics,
            ),
        },

        "latest_balance_sheet_snapshot": {
            **build_snapshot_context(
                snapshot_metrics
            ),
        },
    }

    try:
        insights = generate_board_insights(
            financial_context,
            question=request.question,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Board Insights generation "
                "failed."
            ),
        ) from exc

    sources = match_cited_sources(
        insights,
        metric_lookup,
    )


    return {
        "insights": insights,
        "sources": sources,
        "data_quality": {
            "as_of_date": (
                financial_context["as_of_date"]
            ),
            "unvalidated_pending_documents": (
                unvalidated_pending_documents
            ),
        },
    }