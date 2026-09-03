import pytest

from app.services.financials.calculations import (
    cash_ratio,
    current_ratio,
    ebitda,
    ebitda_margin,
    free_cash_flow,
    gross_margin,
    growth_rate,
    operating_margin,
    revenue_per_employee,
    working_capital,
)


FY2025_METRICS = {
    "revenue": 836991,
    "gross_profit": 648450,
    "operating_profit": -633694,
    "depreciation": 20381,
    "operating_cash_flow": -374820,
    "capex": 4451,
    "cash": 140135,
    "current_assets": 263138,
    "current_liabilities": 243846,
    "employees": 18,
}


FY2024_METRICS = {
    "revenue": 688317,
    "gross_profit": 432477,
    "operating_profit": -1130729,
    "depreciation": 19412,
    "operating_cash_flow": -1166697,
    "capex": 37350,
    "cash": 424639,
    "current_assets": 599369,
    "current_liabilities": 90078,
    "employees": 19,
}


def test_revenue_growth():
    result = growth_rate(
        FY2025_METRICS["revenue"],
        FY2024_METRICS["revenue"],
    )

    assert result == pytest.approx(
        0.2159964086,
    )


def test_gross_margin():
    result = gross_margin(
        FY2025_METRICS
    )

    assert result == pytest.approx(
        0.7747395133,
    )


def test_operating_margin():
    result = operating_margin(
        FY2025_METRICS
    )

    assert result == pytest.approx(
        -0.7571096941,
    )


def test_ebitda():
    result = ebitda(
        FY2025_METRICS
    )

    assert result == -613313


def test_ebitda_margin():
    result = ebitda_margin(
        FY2025_METRICS
    )

    assert result == pytest.approx(
        -0.7327593726,
    )


def test_free_cash_flow():
    result = free_cash_flow(
        FY2025_METRICS
    )

    assert result == -379271


def test_working_capital():
    result = working_capital(
        FY2025_METRICS
    )

    assert result == 19292


def test_current_ratio():
    result = current_ratio(
        FY2025_METRICS
    )

    assert result == pytest.approx(
        1.0791155073,
    )


def test_cash_ratio():
    result = cash_ratio(
        FY2025_METRICS
    )

    assert result == pytest.approx(
        0.5746864825,
    )


def test_revenue_per_employee():
    result = revenue_per_employee(
        FY2025_METRICS
    )

    assert result == pytest.approx(
        46499.5,
    )


def test_growth_rate_returns_none_without_previous_value():
    result = growth_rate(
        FY2025_METRICS["revenue"],
        None,
    )

    assert result is None


def test_current_ratio_returns_none_without_liabilities():
    metrics = {
        "current_assets": 263138,
    }

    assert current_ratio(metrics) is None


def test_cash_ratio_returns_none_without_liabilities():
    metrics = {
        "cash": 140135,
    }

    assert cash_ratio(metrics) is None


def test_revenue_per_employee_returns_none_without_employee_count():
    metrics = {
        "revenue": 836991,
    }

    assert (
        revenue_per_employee(
            metrics
        )
        is None
    )