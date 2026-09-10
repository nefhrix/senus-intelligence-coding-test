import json
import re

from ollama import Client

from app.core.config import settings

NUMBER_IN_TEXT = re.compile(
    r"-?\d[\d,]*(?:\.\d+)?"
)

def match_cited_sources(
    response_text: str,
    metric_lookup: list[dict],
    tolerance: float = 0.5,
) -> list[dict]:
    """
    Given the model's response text and a flat list of metric entries,
    return the subset whose values are actually referenced in the response.
    """

    cited: list[dict] = []
    seen: set[tuple] = set()

    for match in NUMBER_IN_TEXT.finditer(response_text):
        token = match.group().replace(",", "")

        try:
            number = float(token)
        except ValueError:
            continue

        # Ignore years such as 2024, 2025 etc.
        if 1900 <= abs(number) <= 2100:
            continue

        # Ignore tiny values
        if abs(number) < 1:
            continue

        for entry in metric_lookup:
            value = entry.get("value")

            if value is None:
                continue

            # Compare absolute values so -590256 matches 590256
            if abs(abs(number) - abs(value)) > tolerance:
                continue

            key = (
                entry["period_code"],
                entry["metric_code"],
            )

            if key in seen:
                continue

            seen.add(key)
            cited.append(entry)

    return cited



client = Client(
    host=settings.ollama_host,
)

SYSTEM_PROMPT = """
You are a financial analyst supporting a company Board of Directors.

You receive financial information that has already been extracted,
validated, and calculated by the application.

Rules:

1. Use only the supplied financial data.
2. Do not invent figures, causes, events, forecasts, or explanations.
3. Do not recalculate financial metrics.
4. Answer the user's specific question directly.
5. Do not give a generic company overview unless the user asks for one.
6. Do not repeat unrelated financial metrics.
7. Clearly distinguish financial-year results from later balance sheet snapshots.
8. Highlight risks or improvements only when relevant to the question.
9. Be concise and specific.
10. Write for a Board and senior management audience.
11. Use plain text.
12. Use short headings only when they improve the answer.
13. Use bullet points when listing risks, priorities, or comparisons.
14. Do not mention being an AI model.
15. If the supplied data cannot answer the question, say that clearly.
16. Base every financial statement, recommendation and conclusion only on
the supplied reported_metrics and derived_metrics.

Do not calculate new financial figures.

When quoting a number, reproduce it exactly as provided.

If there is insufficient information to answer confidently, state that
clearly.
17. If "as_of_date" is provided and the most recent financial data is
    more than a few months older than that date, note that the data may
    be out of date before drawing conclusions from it.
18. If "unvalidated_pending_documents" is non-empty, mention that more
    recent financial information may exist but has not yet passed
    validation, and is therefore not reflected in this answer.
    19. When the user asks for a recommendation or decision
(e.g. raise funding, hire staff, cut costs),
provide a clear recommendation first,
then justify it using only the supplied financial data.
Avoid generic "it depends" answers unless the data genuinely
cannot support a recommendation.
"""


def generate_board_insights(
    financial_context: dict,
    question: str | None = None,
) -> str:
    if question:
        prompt = f"""
Answer this financial question:

{question}

Respond specifically to this question.

Do not provide a general Board report unless the question explicitly asks
for a full overview.

Focus only on the financial information relevant to the question.

FINANCIAL CONTEXT:

{json.dumps(financial_context, indent=2)}
"""
    else:
        prompt = f"""
Prepare a concise Board-level overview of the financial position.

Cover:

- Growth and revenue
- Profitability
- Cash and liquidity
- Balance sheet strength
- Key financial risks
- Management priorities

FINANCIAL CONTEXT:

{json.dumps(financial_context, indent=2)}
"""

    response = client.chat(
        model=settings.ollama_model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        think=False,
        keep_alive="10m",
        options={
            "temperature": 0.3,
            "num_ctx": 8192,
            "num_predict": 1000,
        },
    )

    content = response.message.content.strip()

    if not content:
        raise RuntimeError(
            "Board Insights generation returned an empty response."
        )

    return content