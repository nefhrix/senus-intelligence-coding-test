from collections import defaultdict

from app.schemas.extraction import (
    ExtractedMetricCandidate,
)


SOURCE_PRIORITY = {
    "cash": [
        "balance_sheet",
        "cash_flow",
    ],
    "net_income": [
        "income_statement",
        "equity_statement",
    ],
}


def approximately_equal(
    first: float,
    second: float,
    tolerance: float = 1.0,
) -> bool:
    return (
        abs(first - second)
        <= tolerance
    )


def select_candidate(
    candidates: list[
        ExtractedMetricCandidate
    ],
) -> ExtractedMetricCandidate:
    metric_code = (
        candidates[0].metric_code
    )

    priority = SOURCE_PRIORITY.get(
        metric_code,
        [],
    )

    def ranking(
        candidate: (
            ExtractedMetricCandidate
        ),
    ):
        try:
            statement_rank = (
                priority.index(
                    candidate.statement_type
                )
            )
        except ValueError:
            statement_rank = 999

        return (
            statement_rank,
            -candidate.confidence,
        )

    return sorted(
        candidates,
        key=ranking,
    )[0]


def validate_and_reconcile(
    candidates: list[
        ExtractedMetricCandidate
    ],
):
    grouped = defaultdict(list)

    for candidate in candidates:
        key = (
            candidate.metric_code,
            candidate.period_label,
        )

        grouped[key].append(
            candidate
        )

    checks = []

    for (
        metric_code,
        period,
    ), group in grouped.items():
        if len(group) < 2:
            continue

        first_value = group[0].value

        passed = all(
            approximately_equal(
                candidate.value,
                first_value,
            )
            for candidate in group[1:]
        )

        checks.append(
            {
                "check": (
                    f"{metric_code}_"
                    f"cross_statement"
                ),
                "period": period,
                "passed": passed,
                "values": [
                    {
                        "value": (
                            candidate.value
                        ),
                        "statement": (
                            candidate.statement_type
                        ),
                    }
                    for candidate in group
                ],
            }
        )

    canonical = [
        select_candidate(group)
        for group in grouped.values()
    ]

    periods = {
        metric.period_label
        for metric in canonical
    }

    if periods == {
    "BS_2025_12_08"
    }:
        canonical.sort(
        key=lambda metric: (
            metric.period_label,
            metric.metric_code,
        )
    )

        return (
            canonical,
            validate_snapshot(
            canonical
            ),
        )

    metric_map = {
        (
            metric.metric_code,
            metric.period_label,
        ): metric.value
        for metric in canonical
    }

    for period in [
        "FY2025",
        "FY2024",
    ]:
        revenue = metric_map.get(
            ("revenue", period)
        )

        cost_of_sales = metric_map.get(
            ("cost_of_sales", period)
        )

        gross_profit = metric_map.get(
            ("gross_profit", period)
        )

        if (
            revenue is not None
            and cost_of_sales is not None
            and gross_profit is not None
        ):
            expected = (
                revenue
                - cost_of_sales
            )

            checks.append(
                {
                    "check": (
                        "gross_profit_"
                        "reconciliation"
                    ),
                    "period": period,
                    "passed": (
                        approximately_equal(
                            expected,
                            gross_profit,
                        )
                    ),
                    "expected": expected,
                    "actual": gross_profit,
                }
            )

        distribution = metric_map.get(
            (
                "distribution_costs",
                period,
            )
        )

        admin = metric_map.get(
            (
                "administrative_expenses",
                period,
            )
        )

        other_income = metric_map.get(
            (
                "other_operating_income",
                period,
            ),
            0.0,
        )

        operating_profit = (
            metric_map.get(
                (
                    "operating_profit",
                    period,
                )
            )
        )

        if (
            gross_profit is not None
            and distribution is not None
            and admin is not None
            and operating_profit
            is not None
        ):
            expected = (
                gross_profit
                - distribution
                - admin
                + other_income
            )

            checks.append(
                {
                    "check": (
                        "operating_profit_"
                        "reconciliation"
                    ),
                    "period": period,
                    "passed": (
                        approximately_equal(
                            expected,
                            operating_profit,
                        )
                    ),
                    "expected": expected,
                    "actual": (
                        operating_profit
                    ),
                }
            )

        debtors = metric_map.get(
            ("debtors", period)
        )

        cash = metric_map.get(
            ("cash", period)
        )

        current_assets = metric_map.get(
            (
                "current_assets",
                period,
            )
        )

        if (
            debtors is not None
            and cash is not None
            and current_assets is not None
        ):
            expected = (
                debtors
                + cash
            )

            checks.append(
                {
                    "check": (
                        "current_assets_"
                        "reconciliation"
                    ),
                    "period": period,
                    "passed": (
                        approximately_equal(
                            expected,
                            current_assets,
                        )
                    ),
                    "expected": expected,
                    "actual": (
                        current_assets
                    ),
                }
            )

    required = {
        "revenue",
        "gross_profit",
        "operating_profit",
        "net_income",
        "cash",
        "debtors",
        "current_assets",
        "current_liabilities",
        "operating_cash_flow",
        "capex",
        "depreciation",
    }

    for period in [
        "FY2025",
        "FY2024",
    ]:
        found = {
            metric.metric_code
            for metric in canonical
            if (
                metric.period_label
                == period
            )
        }

        missing = sorted(
            required - found
        )

        checks.append(
            {
                "check": (
                    "required_metrics"
                ),
                "period": period,
                "passed": (
                    len(missing) == 0
                ),
                "missing": missing,
            }
        )

    passed = all(
        check["passed"]
        for check in checks
    )

    canonical.sort(
        key=lambda metric: (
            metric.period_label,
            metric.metric_code,
        )
    )

    return (
        canonical,
        {
            "status": (
                "validated"
                if passed
                else "needs_review"
            ),
            "checks": checks,
        },
    )

def validate_snapshot(
    metrics: list[
        ExtractedMetricCandidate
    ],
) -> dict:
    values = {
        metric.metric_code: (
            metric.value
        )
        for metric in metrics
        if (
            metric.period_label
            == "BS_2025_12_08"
        )
    }

    required = {
        "cash",
        "debtors",
        "current_assets",
        "current_liabilities",
        "long_term_liabilities",
        "net_assets",
    }

    missing = (
        required
        - set(values.keys())
    )

    checks = []

    checks.append(
        {
            "name": (
                "snapshot_required_metrics"
            ),
            "passed": not missing,
            "missing": sorted(
                missing
            ),
        }
    )

    if {
        "cash",
        "debtors",
        "current_assets",
    }.issubset(values):
        expected = (
            values["cash"]
            + values["debtors"]
        )

        actual = (
            values[
                "current_assets"
            ]
        )

        checks.append(
            {
                "name": (
                    "current_assets_reconciliation"
                ),
                "passed": (
                    abs(
                        expected
                        - actual
                    )
                    <= 1
                ),
                "expected": expected,
                "actual": actual,
            }
        )

    status = (
        "validated"
        if all(
            check["passed"]
            for check in checks
        )
        else "needs_review"
    )

    return {
        "status": status,
        "checks": checks,
    }