MetricMap = dict[str, float]


def safe_divide(
    numerator: float | None,
    denominator: float | None,
) -> float | None:
    if numerator is None:
        return None

    if denominator is None or denominator == 0:
        return None

    return numerator / denominator


def growth_rate(
    current: float | None,
    previous: float | None,
) -> float | None:
    if current is None:
        return None

    if previous is None or previous == 0:
        return None

    return (current - previous) / abs(previous)


def gross_margin(metrics: MetricMap) -> float | None:
    return safe_divide(
        metrics.get("gross_profit"),
        metrics.get("revenue"),
    )


def operating_margin(metrics: MetricMap) -> float | None:
    return safe_divide(
        metrics.get("operating_profit"),
        metrics.get("revenue"),
    )


def ebitda(metrics: MetricMap) -> float | None:
    operating_profit = metrics.get("operating_profit")
    depreciation = metrics.get("depreciation")

    if operating_profit is None or depreciation is None:
        return None

    return operating_profit + depreciation


def ebitda_margin(metrics: MetricMap) -> float | None:
    return safe_divide(
        ebitda(metrics),
        metrics.get("revenue"),
    )


def net_margin(metrics: MetricMap) -> float | None:
    return safe_divide(
        metrics.get("net_income"),
        metrics.get("revenue"),
    )


def free_cash_flow(metrics: MetricMap) -> float | None:
    operating_cash_flow = metrics.get(
        "operating_cash_flow"
    )

    capex = metrics.get("capex")

    if operating_cash_flow is None or capex is None:
        return None

    return operating_cash_flow - capex


def working_capital(metrics: MetricMap) -> float | None:
    current_assets = metrics.get("current_assets")
    current_liabilities = metrics.get(
        "current_liabilities"
    )

    if (
        current_assets is None
        or current_liabilities is None
    ):
        return None

    return current_assets - current_liabilities


def current_ratio(metrics: MetricMap) -> float | None:
    return safe_divide(
        metrics.get("current_assets"),
        metrics.get("current_liabilities"),
    )


def cash_ratio(metrics: MetricMap) -> float | None:
    return safe_divide(
        metrics.get("cash"),
        metrics.get("current_liabilities"),
    )


def revenue_per_employee(
    metrics: MetricMap,
) -> float | None:
    return safe_divide(
        metrics.get("revenue"),
        metrics.get("employees"),
    )