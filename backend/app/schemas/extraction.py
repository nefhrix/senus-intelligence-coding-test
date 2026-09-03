from typing import Literal

from pydantic import BaseModel, Field


StatementType = Literal[
    "income_statement",
    "balance_sheet",
    "cash_flow",
    "equity_statement",
    "notes",
]

MetricCode = Literal[
    "revenue",
    "cost_of_sales",
    "gross_profit",
    "distribution_costs",
    "administrative_expenses",
    "other_operating_income",
    "operating_profit",
    "depreciation",
    "interest_expense",
    "net_income",
    "cash",
    "debtors",
    "current_assets",
    "current_liabilities",
    "long_term_liabilities",
    "net_assets",
    "operating_cash_flow",
    "capex",
    "employees",
    "customers",
]


class FinancialSection(BaseModel):
    statement_type: StatementType
    page_number: int
    title: str
    html: str


class ExtractedMetricCandidate(BaseModel):
    metric_code: MetricCode
    value: float
    period_label: str
    currency: str | None = None
    unit: Literal["EUR", "count"]
    statement_type: StatementType
    source_page: int
    source_text: str = Field(
        min_length=1,
        max_length=500,
    )
    confidence: float = Field(
        ge=0,
        le=1,
    )


class ExtractionResult(BaseModel):
    metrics: list[ExtractedMetricCandidate]