from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.reporting_period import ReportingPeriod
from app.models.reported_metric import ReportedMetric

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
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


def load_metrics(
    db: Session,
    period_id: int,
) -> dict[str, float]:
    rows = (
        db.query(ReportedMetric)
        .filter(ReportedMetric.period_id == period_id)
        .all()
    )

    return {
        row.metric_code: row.value
        for row in rows
    }


@router.get("/{period_code}")
def get_dashboard(
    period_code: str,
    db: Session = Depends(get_db),
):
    period = (
        db.query(ReportingPeriod)
        .filter(ReportingPeriod.code == period_code)
        .first()
    )

    if period is None:
        raise HTTPException(
            status_code=404,
            detail="Reporting period not found",
        )

    if period.period_type != "financial_year":
        raise HTTPException(
            status_code=400,
            detail="A full financial-year period is required.",
        )

    metrics = load_metrics(db, period.id)

    previous_period = (
        db.query(ReportingPeriod)
        .filter(
            ReportingPeriod.company_id == period.company_id,
            ReportingPeriod.period_type == "financial_year",
            ReportingPeriod.end_date < period.end_date,
        )
        .order_by(ReportingPeriod.end_date.desc())
        .first()
    )

    previous_metrics: dict[str, float] = {}

    if previous_period:
        previous_metrics = load_metrics(
            db,
            previous_period.id,
        )

    return {
        "period": {
            "code": period.code,
            "label": period.label,
            "start_date": period.start_date,
            "end_date": period.end_date,
        },
        "kpis": {
            "revenue": {
                "value": metrics.get("revenue"),
                "unit": "EUR",
                "change": growth_rate(
                    metrics.get("revenue"),
                    previous_metrics.get("revenue"),
                ),
            },
            "gross_margin": {
                "value": gross_margin(metrics),
                "unit": "ratio",
            },
            "operating_margin": {
                "value": operating_margin(metrics),
                "unit": "ratio",
            },
            "ebitda": {
                "value": ebitda(metrics),
                "unit": "EUR",
            },
            "ebitda_margin": {
                "value": ebitda_margin(metrics),
                "unit": "ratio",
            },
            "operating_cash_flow": {
                "value": metrics.get("operating_cash_flow"),
                "unit": "EUR",
            },
            "free_cash_flow": {
                "value": free_cash_flow(metrics),
                "unit": "EUR",
            },
            "cash": {
                "value": metrics.get("cash"),
                "unit": "EUR",
            },
            "working_capital": {
                "value": working_capital(metrics),
                "unit": "EUR",
            },
            "current_ratio": {
                "value": current_ratio(metrics),
                "unit": "multiple",
            },
            "cash_ratio": {
                "value": cash_ratio(metrics),
                "unit": "multiple",
            },
            "revenue_per_employee": {
                "value": revenue_per_employee(metrics),
                "unit": "EUR",
            },
        },
    }