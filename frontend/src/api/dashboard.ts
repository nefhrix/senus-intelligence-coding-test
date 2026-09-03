import { API_URL } from "../config";
export type DashboardKpi = {
  value: number | null;
  unit: "EUR" | "ratio" | "multiple";
  change?: number | null;
};

export type DashboardResponse = {
  period: {
    code: string;
    label: string;
    start_date: string | null;
    end_date: string;
  };
  kpis: {
    revenue: DashboardKpi;
    gross_margin: DashboardKpi;
    operating_margin: DashboardKpi;
    ebitda: DashboardKpi;
    ebitda_margin: DashboardKpi;
    operating_cash_flow: DashboardKpi;
    free_cash_flow: DashboardKpi;
    cash: DashboardKpi;
    working_capital: DashboardKpi;
    current_ratio: DashboardKpi;
    cash_ratio: DashboardKpi;
    revenue_per_employee: DashboardKpi;
  };
};

export async function getDashboard(
  periodCode: string,
): Promise<DashboardResponse> {
  const response = await fetch(
    `${API_URL}/api/dashboard/${periodCode}`,
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load dashboard: ${response.status}`,
    );
  }

  return response.json();
}

export type ReportedMetric = {
  metric: string;
  value: number;
  currency: string | null;
  unit: string;
  statement_type: string;
  source_page: number;
  validation_status: string;
};

export type ReportedMetricsResponse = {
  period: {
    code: string;
    label: string;
    period_type: string;
  };
  reported_metrics: ReportedMetric[];
};

export async function getReportedMetrics(
  periodCode: string,
): Promise<ReportedMetricsResponse> {
  const response = await fetch(
    `${API_URL}/api/reported-metrics/${periodCode}`,
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load reported metrics: ${response.status}`,
    );
  }

  return response.json();
}