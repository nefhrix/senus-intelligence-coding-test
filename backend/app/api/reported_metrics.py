from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.reporting_period import ReportingPeriod
from app.models.reported_metric import ReportedMetric


router = APIRouter(
    prefix="/api",
    tags=["Reported Metrics"],
)


@router.get("/periods")
def get_periods(db: Session = Depends(get_db)):
    periods = (
        db.query(ReportingPeriod)
        .order_by(ReportingPeriod.end_date)
        .all()
    )

    return [
        {
            "id": period.id,
            "code": period.code,
            "label": period.label,
            "period_type": period.period_type,
            "start_date": period.start_date,
            "end_date": period.end_date,
        }
        for period in periods
    ]


@router.get("/reported-metrics/{period_code}")
def get_reported_metrics(
    period_code: str,
    db: Session = Depends(get_db),
):
    period = (
        db.query(ReportingPeriod)
        .filter(ReportingPeriod.code == period_code)
        .first()
    )

    if not period:
        raise HTTPException(
            status_code=404,
            detail="Reporting period not found",
        )

    metrics = (
        db.query(ReportedMetric)
        .filter(ReportedMetric.period_id == period.id)
        .all()
    )

    return {
        "period": {
            "code": period.code,
            "label": period.label,
            "period_type": period.period_type,
        },
        "reported_metrics": [
            {
                "metric": metric.metric_code,
                "value": metric.value,
                "currency": metric.currency,
                "unit": metric.unit,
                "statement_type": metric.statement_type,
                "source_page": metric.source_page,
                "validation_status": metric.validation_status,
            }
            for metric in metrics
        ],
    }