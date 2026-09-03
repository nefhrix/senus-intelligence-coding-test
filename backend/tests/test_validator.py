from app.schemas.extraction import ExtractedMetricCandidate

from app.services.extraction.validator import (
    approximately_equal,
    select_candidate,
    validate_and_reconcile,
    validate_snapshot,
)


def candidate(
    metric_code: str,
    value: float,
    period: str,
    statement_type: str,
    confidence: float = 0.99,
) -> ExtractedMetricCandidate:
    return ExtractedMetricCandidate(
        metric_code=metric_code,
        value=value,
        period_label=period,
        currency="EUR",
        unit="EUR",
        statement_type=statement_type,
        source_page=1,
        source_text=f"{metric_code}: {value}",
        confidence=confidence,
    )


def annual_candidates():
    return [
        candidate(
            "revenue",
            688317,
            "FY2024",
            "income_statement",
        ),
        candidate(
            "gross_profit",
            432477,
            "FY2024",
            "income_statement",
        ),
        candidate(
            "operating_profit",
            -1130729,
            "FY2024",
            "income_statement",
        ),
        candidate(
            "net_income",
            -1098095,
            "FY2024",
            "income_statement",
        ),
        candidate(
            "cash",
            424639,
            "FY2024",
            "balance_sheet",
        ),
        candidate(
            "debtors",
            174730,
            "FY2024",
            "balance_sheet",
        ),
        candidate(
            "current_assets",
            599369,
            "FY2024",
            "balance_sheet",
        ),
        candidate(
            "current_liabilities",
            90078,
            "FY2024",
            "balance_sheet",
        ),
        candidate(
            "operating_cash_flow",
            -1166697,
            "FY2024",
            "cash_flow",
        ),
        candidate(
            "capex",
            37350,
            "FY2024",
            "cash_flow",
        ),
        candidate(
            "depreciation",
            19412,
            "FY2024",
            "cash_flow",
        ),
        candidate(
            "revenue",
            836991,
            "FY2025",
            "income_statement",
        ),
        candidate(
            "gross_profit",
            648450,
            "FY2025",
            "income_statement",
        ),
        candidate(
            "operating_profit",
            -633694,
            "FY2025",
            "income_statement",
        ),
        candidate(
            "net_income",
            -590256,
            "FY2025",
            "income_statement",
        ),
        candidate(
            "cash",
            140135,
            "FY2025",
            "balance_sheet",
        ),
        candidate(
            "debtors",
            123003,
            "FY2025",
            "balance_sheet",
        ),
        candidate(
            "current_assets",
            263138,
            "FY2025",
            "balance_sheet",
        ),
        candidate(
            "current_liabilities",
            243846,
            "FY2025",
            "balance_sheet",
        ),
        candidate(
            "operating_cash_flow",
            -374820,
            "FY2025",
            "cash_flow",
        ),
        candidate(
            "capex",
            4451,
            "FY2025",
            "cash_flow",
        ),
        candidate(
            "depreciation",
            20381,
            "FY2025",
            "cash_flow",
        ),
    ]


def snapshot_candidates():
    return [
        candidate(
            "cash",
            528379,
            "BS_2025_12_08",
            "balance_sheet",
        ),
        candidate(
            "debtors",
            261713,
            "BS_2025_12_08",
            "balance_sheet",
        ),
        candidate(
            "current_assets",
            790092,
            "BS_2025_12_08",
            "balance_sheet",
        ),
        candidate(
            "current_liabilities",
            276030,
            "BS_2025_12_08",
            "balance_sheet",
        ),
        candidate(
            "long_term_liabilities",
            79155,
            "BS_2025_12_08",
            "balance_sheet",
        ),
        candidate(
            "net_assets",
            473023,
            "BS_2025_12_08",
            "balance_sheet",
        ),
    ]


def test_approximately_equal_within_tolerance():
    assert approximately_equal(
        100,
        100.5,
    )


def test_approximately_equal_outside_tolerance():
    assert not approximately_equal(
        100,
        102,
    )


def test_cash_prefers_balance_sheet():
    cash_flow = candidate(
        "cash",
        140135,
        "FY2025",
        "cash_flow",
        confidence=1.0,
    )

    balance_sheet = candidate(
        "cash",
        140135,
        "FY2025",
        "balance_sheet",
        confidence=0.90,
    )

    selected = select_candidate(
        [
            cash_flow,
            balance_sheet,
        ]
    )

    assert (
        selected.statement_type
        == "balance_sheet"
    )


def test_net_income_prefers_income_statement():
    equity = candidate(
        "net_income",
        -590256,
        "FY2025",
        "equity_statement",
        confidence=1.0,
    )

    income_statement = candidate(
        "net_income",
        -590256,
        "FY2025",
        "income_statement",
        confidence=0.90,
    )

    selected = select_candidate(
        [
            equity,
            income_statement,
        ]
    )

    assert (
        selected.statement_type
        == "income_statement"
    )


def test_higher_confidence_used_without_source_priority():
    lower_confidence = candidate(
        "revenue",
        836991,
        "FY2025",
        "income_statement",
        confidence=0.80,
    )

    higher_confidence = candidate(
        "revenue",
        836991,
        "FY2025",
        "income_statement",
        confidence=0.99,
    )

    selected = select_candidate(
        [
            lower_confidence,
            higher_confidence,
        ]
    )

    assert selected.confidence == 0.99


def test_valid_annual_metrics_are_validated():
    canonical, validation = (
        validate_and_reconcile(
            annual_candidates()
        )
    )

    assert (
        validation["status"]
        == "validated"
    )

    assert len(canonical) == 22

    assert all(
        check["passed"]
        for check in validation[
            "checks"
        ]
    )


def test_missing_required_metric_needs_review():
    metrics = [
        metric
        for metric in annual_candidates()
        if not (
            metric.period_label
            == "FY2025"
            and metric.metric_code
            == "capex"
        )
    ]

    _, validation = (
        validate_and_reconcile(
            metrics
        )
    )

    assert (
        validation["status"]
        == "needs_review"
    )

    required_check = next(
        check
        for check in validation[
            "checks"
        ]
        if (
            check["check"]
            == "required_metrics"
            and check["period"]
            == "FY2025"
        )
    )

    assert not required_check[
        "passed"
    ]

    assert "capex" in required_check[
        "missing"
    ]


def test_current_assets_mismatch_needs_review():
    metrics = annual_candidates()

    for metric in metrics:
        if (
            metric.period_label
            == "FY2025"
            and metric.metric_code
            == "current_assets"
        ):
            metric.value = 300000

    _, validation = (
        validate_and_reconcile(
            metrics
        )
    )

    assert (
        validation["status"]
        == "needs_review"
    )

    check = next(
        check
        for check in validation[
            "checks"
        ]
        if (
            check["check"]
            == "current_assets_reconciliation"
            and check["period"]
            == "FY2025"
        )
    )

    assert not check["passed"]
    assert check["expected"] == 263138
    assert check["actual"] == 300000


def test_conflicting_cross_statement_value_needs_review():
    metrics = annual_candidates()

    metrics.append(
        candidate(
            "cash",
            150000,
            "FY2025",
            "cash_flow",
        )
    )

    canonical, validation = (
        validate_and_reconcile(
            metrics
        )
    )

    assert (
        validation["status"]
        == "needs_review"
    )

    cross_statement_check = next(
        check
        for check in validation[
            "checks"
        ]
        if (
            check["check"]
            == "cash_cross_statement"
            and check["period"]
            == "FY2025"
        )
    )

    assert not cross_statement_check[
        "passed"
    ]

    canonical_cash = next(
        metric
        for metric in canonical
        if (
            metric.metric_code
            == "cash"
            and metric.period_label
            == "FY2025"
        )
    )

    assert canonical_cash.value == 140135
    assert (
        canonical_cash.statement_type
        == "balance_sheet"
    )


def test_valid_snapshot_is_validated():
    validation = validate_snapshot(
        snapshot_candidates()
    )

    assert (
        validation["status"]
        == "validated"
    )

    assert all(
        check["passed"]
        for check in validation[
            "checks"
        ]
    )


def test_snapshot_missing_metric_needs_review():
    metrics = [
        metric
        for metric in snapshot_candidates()
        if metric.metric_code
        != "long_term_liabilities"
    ]

    validation = validate_snapshot(
        metrics
    )

    assert (
        validation["status"]
        == "needs_review"
    )

    required_check = next(
        check
        for check in validation[
            "checks"
        ]
        if (
            check["name"]
            == "snapshot_required_metrics"
        )
    )

    assert (
        "long_term_liabilities"
        in required_check["missing"]
    )


def test_snapshot_current_assets_must_reconcile():
    metrics = snapshot_candidates()

    for metric in metrics:
        if (
            metric.metric_code
            == "current_assets"
        ):
            metric.value = 800000

    validation = validate_snapshot(
        metrics
    )

    assert (
        validation["status"]
        == "needs_review"
    )

    reconciliation = next(
        check
        for check in validation[
            "checks"
        ]
        if (
            check["name"]
            == "current_assets_reconciliation"
        )
    )

    assert not reconciliation[
        "passed"
    ]

    assert (
        reconciliation["expected"]
        == 790092
    )

    assert (
        reconciliation["actual"]
        == 800000
    )


def test_snapshot_routes_through_main_validator():
    canonical, validation = (
        validate_and_reconcile(
            snapshot_candidates()
        )
    )

    assert (
        validation["status"]
        == "validated"
    )

    assert len(canonical) == 6