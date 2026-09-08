from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReportedMetric(Base):
    __tablename__ = "reported_metrics"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "period_id",
            "metric_code",
            name="uq_reported_metric_company_period_metric",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    period_id: Mapped[int] = mapped_column(
        ForeignKey("reporting_periods.id"),
        nullable=False,
        index=True,
    )

    metric_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    currency: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    statement_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_page: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    source_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    validation_status: Mapped[str] = mapped_column(
        String(50),
        default="validated",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )