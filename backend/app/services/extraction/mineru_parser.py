import json
import re
from pathlib import Path

from app.schemas.extraction import FinancialSection


STATEMENT_PATTERNS = {
    "income_statement": (
        "consolidated profit and loss account",
        "group profit and loss account",
        "profit and loss account",
        "consolidated income statement",
        "income statement",
        "consolidated statement of comprehensive income",
        "statement of comprehensive income",
    ),
    "balance_sheet": (
        "consolidated balance sheet",
        "group balance sheet",
        "balance sheet",
        "consolidated statement of financial position",
        "statement of financial position",
    ),
    "cash_flow": (
        "consolidated statement of cash flows",
        "group statement of cash flows",
        "statement of cash flows",
        "consolidated cash flow statement",
        "cash flow statement",
    ),
    "equity_statement": (
        "consolidated statement of changes in equity",
        "group statement of changes in equity",
        "statement of changes in equity",
    ),
}


STATEMENT_ORDER = (
    "income_statement",
    "balance_sheet",
    "cash_flow",
    "equity_statement",
)


def normalize_text(value: str) -> str:
    value = value.lower()
    value = value.replace("balancesheet", "balance sheet")
    value = re.sub(r"[^a-z0-9]+", " ", value)

    return " ".join(value.split())


def spans_to_text(
    spans: list[dict],
) -> str:
    values = []

    for span in spans:
        content = span.get("content")

        if isinstance(content, str):
            content = content.strip()

            if content:
                values.append(content)

    return " ".join(values)


def get_title_text(
    block: dict,
) -> str:
    content = block.get("content", {})
    title_content = content.get(
        "title_content",
        [],
    )

    return spans_to_text(title_content)


def get_table_caption(
    block: dict,
) -> str:
    content = block.get("content", {})
    caption = content.get(
        "table_caption",
        [],
    )

    return spans_to_text(caption)


def classify_statement(
    value: str,
) -> str | None:
    normalized = normalize_text(value)

    if re.fullmatch(
        r"\d+\s+income statement",
        normalized,
    ):
        return None

    if (
        "notes to the balance sheet"
        in normalized
        or "notes to the financial statements"
        in normalized
    ):
        return None

    for statement_type, patterns in (
        STATEMENT_PATTERNS.items()
    ):
        for pattern in patterns:
            if pattern in normalized:
                return statement_type

    return None


def parse_financial_sections(
    file_path: str | Path,
) -> list[FinancialSection]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"MinerU output not found: {path}"
        )

    raw = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(raw, list):
        raise ValueError(
            "MinerU content_list_v2 must be a list."
        )

    found: dict[
        str,
        FinancialSection,
    ] = {}

    for page_index, page in enumerate(
        raw
    ):
        if not isinstance(page, list):
            continue

        current_title = ""

        for block in page:
            if not isinstance(block, dict):
                continue

            block_type = block.get("type")

            if block_type == "title":
                current_title = get_title_text(
                    block
                )
                continue

            if block_type != "table":
                continue

            content = block.get(
                "content",
                {},
            )

            html = content.get("html")

            if not isinstance(
                html,
                str,
            ):
                continue

            caption = get_table_caption(
                block
            )

            label = (
                caption
                or current_title
            )

            statement_type = (
                classify_statement(
                    label
                )
            )

            if statement_type is None:
                continue

            if statement_type in found:
                continue

            found[statement_type] = (
                FinancialSection(
                    statement_type=statement_type,
                    page_number=(
                        page_index + 1
                    ),
                    title=label,
                    html=html,
                )
            )

    return [
        found[statement_type]
        for statement_type
        in STATEMENT_ORDER
        if statement_type in found
    ]