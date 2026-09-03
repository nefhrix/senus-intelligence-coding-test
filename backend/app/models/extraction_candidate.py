from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.base import Base


class ExtractionCandidate(Base):
    __tablename__ = "extraction_candidates"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "period_code",
            "metric_code",
            name="uq_candidate_document_period_metric",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
    )

    period_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    metric_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    statement_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_page: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    source_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    validation_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )