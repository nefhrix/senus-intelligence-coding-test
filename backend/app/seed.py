from datetime import date

from app.db.session import SessionLocal

from app.models.company import Company
from app.models.document import Document
from app.models.reporting_period import ReportingPeriod
from app.models.reported_metric import ReportedMetric



def reported_metric(
    company_id: int,
    document_id: int,
    period_id: int,
    metric_code: str,
    value: float,
    statement_type: str,
    source_page: int,
    unit: str = "EUR",
    currency: str | None = "EUR",
):
    return ReportedMetric(
        company_id=company_id,
        document_id=document_id,
        period_id=period_id,
        metric_code=metric_code,
        value=value,
        currency=currency,
        unit=unit,
        statement_type=statement_type,
        source_page=source_page,
        confidence=1.0,
        validation_status="validated",
    )


def seed():
    db = SessionLocal()

    try:
        existing = (
            db.query(Company)
            .filter(Company.name == "Senus PLC")
            .first()
        )

        if existing:
            print("Database already seeded.")
            return

        # -------------------------
        # Company
        # -------------------------

        company = Company(
            name="Senus PLC",
            ticker=None,
            currency="EUR",
        )

        db.add(company)
        db.flush()

        # -------------------------
        # Documents
        # -------------------------

        annual_report = Document(
            company_id=company.id,
            name="Consolidated Financial Statements 30 June 2025",
            document_type="annual_report",
            status="processed",
        )

        december_balance_sheet = Document(
            company_id=company.id,
            name="Company Balance Sheet as at 8 December 2025",
            document_type="balance_sheet",
            status="processed",
        )

        db.add_all([
            annual_report,
            december_balance_sheet,
        ])

        db.flush()

        # -------------------------
        # Reporting periods
        # -------------------------

        fy2024 = ReportingPeriod(
            company_id=company.id,
            code="FY2024",
            label="FY 2024",
            period_type="financial_year",
            start_date=date(2023, 7, 1),
            end_date=date(2024, 6, 30),
        )

        fy2025 = ReportingPeriod(
            company_id=company.id,
            code="FY2025",
            label="FY 2025",
            period_type="financial_year",
            start_date=date(2024, 7, 1),
            end_date=date(2025, 6, 30),
        )

        dec2025 = ReportingPeriod(
            company_id=company.id,
            code="BS_2025_12_08",
            label="8 Dec 2025",
            period_type="balance_sheet_snapshot",
            start_date=None,
            end_date=date(2025, 12, 8),
        )

        db.add_all([
            fy2024,
            fy2025,
            dec2025,
        ])

        db.flush()


        metrics = [
            # ---------------------
            # FY2024
            # ---------------------

            reported_metric(
                company.id,
                annual_report.id,
                fy2024.id,
                "revenue",
                688317,
                "income_statement",
                10,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2024.id,
                "cost_of_sales",
                255840,
                "income_statement",
                10,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2024.id,
                "gross_profit",
                432477,
                "income_statement",
                10,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2024.id,
                "operating_profit",
                -1130729,
                "income_statement",
                10,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2024.id,
                "cash",
                424639,
                "balance_sheet",
                11,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2024.id,
                "operating_cash_flow",
                -1166697,
                "cash_flow",
                15,
            ),

            # ---------------------
            # FY2025
            # ---------------------

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "revenue",
                836991,
                "income_statement",
                10,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "cost_of_sales",
                188541,
                "income_statement",
                10,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "gross_profit",
                648450,
                "income_statement",
                10,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "operating_profit",
                -633694,
                "income_statement",
                10,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "depreciation",
                20381,
                "notes",
                18,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "net_income",
                -590256,
                "income_statement",
                10,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "cash",
                140135,
                "balance_sheet",
                11,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "current_assets",
                263138,
                "balance_sheet",
                11,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "current_liabilities",
                243846,
                "balance_sheet",
                11,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "long_term_liabilities",
                83655,
                "balance_sheet",
                11,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "operating_cash_flow",
                -374820,
                "cash_flow",
                15,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "capex",
                4451,
                "cash_flow",
                15,
            ),

            reported_metric(
                company.id,
                annual_report.id,
                fy2025.id,
                "employees",
                18,
                "notes",
                19,
                unit="count",
                currency=None,
            ),

            # ---------------------
            # December 2025
            # ---------------------

            reported_metric(
                company.id,
                december_balance_sheet.id,
                dec2025.id,
                "cash",
                528379,
                "balance_sheet",
                6,
            ),

            reported_metric(
                company.id,
                december_balance_sheet.id,
                dec2025.id,
                "debtors",
                261713,
                "balance_sheet",
                6,
            ),

            reported_metric(
                company.id,
                december_balance_sheet.id,
                dec2025.id,
                "current_assets",
                790092,
                "balance_sheet",
                6,
            ),

            reported_metric(
                company.id,
                december_balance_sheet.id,
                dec2025.id,
                "current_liabilities",
                276030,
                "balance_sheet",
                6,
            ),

            reported_metric(
                company.id,
                december_balance_sheet.id,
                dec2025.id,
                "long_term_liabilities",
                79155,
                "balance_sheet",
                6,
            ),

            reported_metric(
                company.id,
                december_balance_sheet.id,
                dec2025.id,
                "net_assets",
                473023,
                "balance_sheet",
                6,
            ),
        ]

        db.add_all(metrics)

        db.commit()

        print("Senus database seeded successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()