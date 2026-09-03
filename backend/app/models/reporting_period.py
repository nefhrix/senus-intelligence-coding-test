from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReportingPeriod(Base):
    __tablename__ = "reporting_periods"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    label: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    period_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )