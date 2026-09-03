import re
from html.parser import HTMLParser

from app.schemas.extraction import (
    ExtractedMetricCandidate,
    ExtractionResult,
    FinancialSection,
)


NUMBER_PATTERN = re.compile(
    r"\(\s*\d[\d,]*(?:\.\d+)?\s*\)"
    r"|-?\d[\d,]*(?:\.\d+)?"
)

POSITIVE_MAGNITUDE_METRICS = {
    "cost_of_sales",
    "distribution_costs",
    "administrative_expenses",
    "depreciation",
    "interest_expense",
    "current_liabilities",
    "long_term_liabilities",
    "capex",
}


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows: list[list[str]] = []
        self.current_row: list[str] | None = None
        self.current_cell: list[str] | None = None

    def handle_starttag(
        self,
        tag: str,
        attrs,
    ):
        if tag == "tr":
            self.current_row = []

        if tag in {"td", "th"}:
            self.current_cell = []

    def handle_data(
        self,
        data: str,
    ):
        if self.current_cell is not None:
            self.current_cell.append(data)

    def handle_endtag(
        self,
        tag: str,
    ):
        if (
            tag in {"td", "th"}
            and self.current_cell is not None
        ):
            value = " ".join(
                "".join(
                    self.current_cell
                ).split()
            )

            if self.current_row is not None:
                self.current_row.append(
                    value
                )

            self.current_cell = None

        if (
            tag == "tr"
            and self.current_row is not None
        ):
            self.rows.append(
                self.current_row
            )
            self.current_row = None


def parse_table_rows(
    html: str,
) -> list[list[str]]:
    parser = TableParser()
    parser.feed(html)
    return parser.rows


def normalize_text(
    value: str,
) -> str:
    value = value.lower()
    value = value.replace("&", "and")
    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value,
    )

    return " ".join(
        value.split()
    )


def parse_numbers(
    value: str,
) -> list[float]:
    results = []

    for match in NUMBER_PATTERN.findall(
        value
    ):
        token = match.strip()

        negative = (
            token.startswith("(")
            or token.startswith("-")
        )

        cleaned = (
            token
            .replace("(", "")
            .replace(")", "")
            .replace(",", "")
            .replace("€", "")
            .replace("-", "")
            .strip()
        )

        if not cleaned:
            continue

        number = float(cleaned)

        if negative:
            number = -number

        results.append(number)

    return results


def single_number(
    value: str,
) -> float | None:
    values = parse_numbers(value)

    if len(values) != 1:
        return None

    return values[0]


def source_text(
    *rows: list[str],
) -> str:
    parts = []

    for row in rows:
        text = " | ".join(
            cell
            for cell in row
            if cell
        )

        if text:
            parts.append(text)

    return " || ".join(parts)[:500]


def find_year_columns(
    rows: list[list[str]],
) -> dict[str, int]:
    columns = {}

    for row in rows[:5]:
        for index, cell in enumerate(row):
            if re.search(
                r"\b2025\b",
                cell,
            ):
                columns["FY2025"] = index

            if re.search(
                r"\b2024\b",
                cell,
            ):
                columns["FY2024"] = index

        if len(columns) == 2:
            break

    return columns


def canonical_value(
    metric_code: str,
    value: float,
) -> float:
    if (
        metric_code
        in POSITIVE_MAGNITUDE_METRICS
    ):
        return abs(value)

    return value


def make_metric(
    section: FinancialSection,
    metric_code: str,
    period_label: str,
    value: float,
    row_source: str,
    confidence: float = 0.99,
) -> ExtractedMetricCandidate:
    return ExtractedMetricCandidate(
        metric_code=metric_code,
        value=canonical_value(
            metric_code,
            value,
        ),
        period_label=period_label,
        currency="EUR",
        unit="EUR",
        statement_type=(
            section.statement_type
        ),
        source_page=section.page_number,
        source_text=row_source,
        confidence=confidence,
    )


def values_by_year(
    row: list[str],
    year_columns: dict[str, int],
) -> dict[str, float]:
    values = {}

    for period, index in (
        year_columns.items()
    ):
        if index >= len(row):
            continue

        value = single_number(
            row[index]
        )

        if value is not None:
            values[period] = value

    return values


def expense_from_cell(
    value: str,
) -> tuple[float | None, float]:
    values = parse_numbers(value)

    if len(values) == 1:
        return values[0], 0.99

    negatives = [
        number
        for number in values
        if number < 0
    ]

    if len(negatives) == 1:
        return negatives[0], 0.90

    return None, 0.0


def extract_income_statement(
    section: FinancialSection,
    rows: list[list[str]],
) -> list[ExtractedMetricCandidate]:
    metrics = []
    year_columns = find_year_columns(
        rows
    )

    mappings = {
        "turnover": "revenue",
        "cost of sales": "cost_of_sales",
        "gross profit": "gross_profit",
        "distribution costs": (
            "distribution_costs"
        ),
        "group operating loss": (
            "operating_profit"
        ),
        "group operating profit": (
            "operating_profit"
        ),
        "loss for the financial year": (
            "net_income"
        ),
        "profit for the financial year": (
            "net_income"
        ),
    }

    for row in rows:
        if not row:
            continue

        label = normalize_text(
            row[0]
        )

        if label in mappings:
            metric_code = mappings[label]

            for (
                period,
                value,
            ) in values_by_year(
                row,
                year_columns,
            ).items():
                metrics.append(
                    make_metric(
                        section,
                        metric_code,
                        period,
                        value,
                        source_text(row),
                    )
                )

        if (
            "administrative expenses"
            in label
        ):
            for (
                period,
                index,
            ) in year_columns.items():
                if index >= len(row):
                    continue

                values = parse_numbers(
                    row[index]
                )

                negatives = [
                    value
                    for value in values
                    if value < 0
                ]

                positives = [
                    value
                    for value in values
                    if value > 0
                ]

                if negatives:
                    metrics.append(
                        make_metric(
                            section,
                            "administrative_expenses",
                            period,
                            negatives[0],
                            source_text(row),
                            0.95,
                        )
                    )

                if (
                    "other operating income"
                    in label
                    and positives
                ):
                    metrics.append(
                        make_metric(
                            section,
                            "other_operating_income",
                            period,
                            positives[0],
                            source_text(row),
                            0.95,
                        )
                    )
    return metrics


def extract_balance_sheet(
    section: FinancialSection,
    rows: list[list[str]],
) -> list[ExtractedMetricCandidate]:
    metrics = []
    year_columns = find_year_columns(
        rows
    )

    debtors = {}
    cash = {}

    debtors_row = None
    cash_row = None
    creditor_row = None
    creditor_index = None

    for index, row in enumerate(rows):
        if not row:
            continue

        label = normalize_text(
            row[0]
        )

        if (
            "current assets"
            in label
            and "debtors"
            in label
        ):
            debtors_row = row
            debtors = values_by_year(
                row,
                year_columns,
            )

            for period, value in (
                debtors.items()
            ):
                metrics.append(
                    make_metric(
                        section,
                        "debtors",
                        period,
                        value,
                        source_text(row),
                    )
                )

        elif (
            "cash and cash equivalents"
            in label
        ):
            cash_row = row
            cash = values_by_year(
                row,
                year_columns,
            )

            for period, value in (
                cash.items()
            ):
                metrics.append(
                    make_metric(
                        section,
                        "cash",
                        period,
                        value,
                        source_text(row),
                    )
                )

        elif (
            "amounts falling due within"
            in label
            and "one year"
            in label
        ):
            creditor_row = row
            creditor_index = index

        elif (
            "amounts falling due after"
            in label
            and "one year"
            in label
        ):
            for (
                period,
                value,
            ) in values_by_year(
                row,
                year_columns,
            ).items():
                metrics.append(
                    make_metric(
                        section,
                        "long_term_liabilities",
                        period,
                        value,
                        source_text(row),
                    )
                )

        elif (
            "net (liabilities)/assets"
            in label
            or label == "net assets"
        ):
            for (
                period,
                value,
            ) in values_by_year(
                row,
                year_columns,
            ).items():
                metrics.append(
                    make_metric(
                        section,
                        "net_assets",
                        period,
                        value,
                        source_text(row),
                    )
                )

    if (
        creditor_row is not None
        and creditor_index is not None
    ):
        creditor_values = values_by_year(
            creditor_row,
            year_columns,
        )

        next_row = None

        if creditor_index + 1 < len(rows):
            next_row = rows[
                creditor_index + 1
            ]

        next_values = {}

        if next_row is not None:
            next_values = values_by_year(
                next_row,
                year_columns,
            )

        for period in {
            "FY2025",
            "FY2024",
        }:
            debtors_value = debtors.get(
                period
            )
            cash_value = cash.get(
                period
            )
            shifted_total = (
                creditor_values.get(
                    period
                )
            )

            if (
                debtors_value is not None
                and cash_value is not None
                and shifted_total
                is not None
            ):
                expected_assets = (
                    debtors_value
                    + cash_value
                )

                if abs(
                    expected_assets
                    - shifted_total
                ) <= 1:
                    metrics.append(
                        make_metric(
                            section,
                            "current_assets",
                            period,
                            shifted_total,
                            source_text(
                                debtors_row or [],
                                cash_row or [],
                                creditor_row,
                            ),
                            0.95,
                        )
                    )

                    liability = (
                        next_values.get(
                            period
                        )
                    )

                    if liability is not None:
                        metrics.append(
                            make_metric(
                                section,
                                "current_liabilities",
                                period,
                                liability,
                                source_text(
                                    creditor_row,
                                    next_row or [],
                                ),
                                0.95,
                            )
                        )

                    continue

            value = creditor_values.get(
                period
            )

            if (
                value is not None
                and value < 0
            ):
                metrics.append(
                    make_metric(
                        section,
                        "current_liabilities",
                        period,
                        value,
                        source_text(
                            creditor_row
                        ),
                        0.90,
                    )
                )

    return metrics

def extract_balance_sheet_snapshot(
    section: FinancialSection,
) -> ExtractionResult:
    rows = parse_table_rows(
        section.html
    )

    metrics = []

    for index, row in enumerate(rows):
        if not row:
            continue

        row_text = normalize_text(
            " ".join(row)
        )

        numbers = parse_numbers(
            " ".join(row)
        )

        if (
            "debtors"
            in row_text
            and "cash and cash equivalents"
            in row_text
            and len(numbers) >= 2
        ):
            metrics.append(
                ExtractedMetricCandidate(
                    metric_code="debtors",
                    value=float(
                        abs(numbers[-2])
                    ),
                    period_label=(
                        "BS_2025_12_08"
                    ),
                    currency="EUR",
                    unit="EUR",
                    statement_type=(
                        "balance_sheet"
                    ),
                    source_page=(
                        section.page_number
                    ),
                    source_text=(
                        source_text(row)
                    ),
                    confidence=0.95,
                )
            )

            metrics.append(
                ExtractedMetricCandidate(
                    metric_code="cash",
                    value=float(
                        abs(numbers[-1])
                    ),
                    period_label=(
                        "BS_2025_12_08"
                    ),
                    currency="EUR",
                    unit="EUR",
                    statement_type=(
                        "balance_sheet"
                    ),
                    source_page=(
                        section.page_number
                    ),
                    source_text=(
                        source_text(row)
                    ),
                    confidence=0.95,
                )
            )

            if index + 1 < len(rows):
                next_row = rows[
                    index + 1
                ]

                next_numbers = (
                    parse_numbers(
                        " ".join(
                            next_row
                        )
                    )
                )

                if next_numbers:
                    metrics.append(
                        ExtractedMetricCandidate(
                            metric_code=(
                                "current_assets"
                            ),
                            value=float(
                                abs(
                                    next_numbers[
                                        -1
                                    ]
                                )
                            ),
                            period_label=(
                                "BS_2025_12_08"
                            ),
                            currency="EUR",
                            unit="EUR",
                            statement_type=(
                                "balance_sheet"
                            ),
                            source_page=(
                                section.page_number
                            ),
                            source_text=(
                                source_text(
                                    next_row
                                )
                            ),
                            confidence=0.95,
                        )
                    )

        elif (
            "creditors amounts falling due within one year"
            in row_text
            and numbers
        ):
            metrics.append(
                ExtractedMetricCandidate(
                    metric_code=(
                        "current_liabilities"
                    ),
                    value=float(
                        abs(numbers[-1])
                    ),
                    period_label=(
                        "BS_2025_12_08"
                    ),
                    currency="EUR",
                    unit="EUR",
                    statement_type=(
                        "balance_sheet"
                    ),
                    source_page=(
                        section.page_number
                    ),
                    source_text=(
                        source_text(row)
                    ),
                    confidence=0.99,
                )
            )

        elif (
            "creditors amounts falling due after more than one year"
            in row_text
            and numbers
        ):
            metrics.append(
                ExtractedMetricCandidate(
                    metric_code=(
                        "long_term_liabilities"
                    ),
                    value=float(
                        abs(numbers[-1])
                    ),
                    period_label=(
                        "BS_2025_12_08"
                    ),
                    currency="EUR",
                    unit="EUR",
                    statement_type=(
                        "balance_sheet"
                    ),
                    source_page=(
                        section.page_number
                    ),
                    source_text=(
                        source_text(row)
                    ),
                    confidence=0.99,
                )
            )

        elif (
            row_text.startswith(
                "net assets"
            )
            and numbers
        ):
            metrics.append(
                ExtractedMetricCandidate(
                    metric_code="net_assets",
                    value=float(
                        numbers[-1]
                    ),
                    period_label=(
                        "BS_2025_12_08"
                    ),
                    currency="EUR",
                    unit="EUR",
                    statement_type=(
                        "balance_sheet"
                    ),
                    source_page=(
                        section.page_number
                    ),
                    source_text=(
                        source_text(row)
                    ),
                    confidence=0.99,
                )
            )

    return ExtractionResult(
        metrics=metrics
    )
def extract_cash_flow(
    section: FinancialSection,
    rows: list[list[str]],
) -> list[ExtractedMetricCandidate]:
    metrics = []
    year_columns = find_year_columns(
        rows
    )

    for row in rows:
        if not row:
            continue

        label = normalize_text(
            row[0]
        )

        metric_code = None

        if (
            "net cash used in operating activities"
            in label
        ):
            metric_code = (
                "operating_cash_flow"
            )

        elif (
            "payments to acquire tangible assets"
            in label
        ):
            metric_code = "capex"

        elif (
            "cash and cash equivalents at end"
            in label
        ):
            metric_code = "cash"

        elif (
            "interest payable and similar expenses"
            in label
        ):
            metric_code = (
                "interest_expense"
            )

        if metric_code is not None:
            for (
                period,
                value,
            ) in values_by_year(
                row,
                year_columns,
            ).items():
                metrics.append(
                    make_metric(
                        section,
                        metric_code,
                        period,
                        value,
                        source_text(row),
                    )
                )

        if label.startswith(
            "depreciation"
        ):
            for (
                period,
                index,
            ) in year_columns.items():
                if index >= len(row):
                    continue

                values = parse_numbers(
                    row[index]
                )

                positives = [
                    value
                    for value in values
                    if value > 0
                ]

                if len(positives) == 1:
                    confidence = (
                        0.90
                        if len(values) > 1
                        else 0.99
                    )

                    metrics.append(
                        make_metric(
                            section,
                            "depreciation",
                            period,
                            positives[0],
                            source_text(row),
                            confidence,
                        )
                    )

    return metrics


def extract_equity_statement(
    section: FinancialSection,
    rows: list[list[str]],
) -> list[ExtractedMetricCandidate]:
    metrics = []
    next_loss_period = "FY2024"

    for row in rows:
        if not row:
            continue

        label = normalize_text(
            row[0]
        )

        if (
            "at 30 june 2024"
            in label
        ):
            next_loss_period = "FY2025"
            continue

        if (
            label
            not in {
                "loss for the financial year",
                "profit for the financial year",
            }
        ):
            continue

        value = None

        for cell in reversed(row[1:]):
            parsed = single_number(
                cell
            )

            if parsed is not None:
                value = parsed
                break

        if value is None:
            continue

        metrics.append(
            make_metric(
                section,
                "net_income",
                next_loss_period,
                value,
                source_text(row),
            )
        )

    return metrics


def extract_deterministic_metrics(
    section: FinancialSection,
) -> ExtractionResult:
    normalized_title = (
        normalize_text(
            section.title
        )
    )

    is_december_snapshot = (
        "balance sheet"
        in normalized_title
        and "08 december 2025"
        in normalized_title
    )

    if is_december_snapshot:
        return (
            extract_balance_sheet_snapshot(
                section
            )
        )

    if (
        "08 december 2025"
        in normalized_title
        and section.statement_type
        == "equity_statement"
    ):
        return ExtractionResult(
            metrics=[]
        )

    if (
        section.statement_type
        == "income_statement"
    ):
        return extract_income_statement(
            section
        )

    if (
        section.statement_type
        == "balance_sheet"
    ):
        return extract_balance_sheet(
            section
        )

    if (
        section.statement_type
        == "cash_flow"
    ):
        return extract_cash_flow(
            section
        )

    if (
        section.statement_type
        == "equity_statement"
    ):
        return extract_equity_statement(
            section
        )

    return ExtractionResult(
        metrics=[]
    )