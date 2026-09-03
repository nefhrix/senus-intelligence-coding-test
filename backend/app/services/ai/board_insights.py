import json
import os

from ollama import Client

from app.core.config import settings



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