from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.reporting_period import ReportingPeriod
from app.models.reported_metric import ReportedMetric

from app.services.ai.board_insights import (
    generate_board_insights,
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

    fy2024_metrics = load_metrics(
        db,
        fy2024.id,
    )

    fy2025_metrics = load_metrics(
        db,
        fy2025.id,
    )

    snapshot_metrics = load_metrics(
        db,
        snapshot.id,
    )

    financial_context = {
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

    return {
        "insights": insights,
    }