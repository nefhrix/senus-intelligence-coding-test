import {
  useQueries,
  useQuery,
} from "@tanstack/react-query";

import {
  getDashboard,
  getReportedMetrics,
  type ReportedMetric,
} from "../api/dashboard";

import {
  formatCurrency,
  formatPercent,
} from "../utils/formatters";

const annualPeriods = [
  {
    code: "FY2024",
    label: "FY 2024",
  },
  {
    code: "FY2025",
    label: "FY 2025",
  },
];

export default function Financials() {
  const dashboardResults = useQueries({
    queries: annualPeriods.map(
      (period) => ({
        queryKey: [
          "dashboard",
          period.code,
        ],
        queryFn: () =>
          getDashboard(period.code),
      }),
    ),
  });

  const annualMetricResults = useQueries({
    queries: annualPeriods.map(
      (period) => ({
        queryKey: [
          "reported-metrics",
          period.code,
        ],
        queryFn: () =>
          getReportedMetrics(
            period.code,
          ),
      }),
    ),
  });

  const snapshotResult = useQuery({
    queryKey: [
      "reported-metrics",
      "BS_2025_12_08",
    ],
    queryFn: () =>
      getReportedMetrics(
        "BS_2025_12_08",
      ),
  });

  const isLoading =
    dashboardResults.some(
      (result) => result.isLoading,
    )
    || annualMetricResults.some(
      (result) => result.isLoading,
    );

  // The FY2024/FY2025 data above is required for this page.
  // The balance-sheet snapshot is supplementary — if it hasn't
  // been uploaded/validated yet, that should only affect the
  // snapshot column, not block the whole page from rendering.
  const isError =
    dashboardResults.some(
      (result) => result.isError,
    )
    || annualMetricResults.some(
      (result) => result.isError,
    );

  if (isLoading) {
    return (
      <div className="flex min-h-96 items-center justify-center">
        <p className="text-sm text-zinc-500">
          Loading financials...
        </p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6">
        <p className="text-sm font-medium text-red-700">
          Unable to load financial data.
        </p>
      </div>
    );
  }

  const annualMetrics =
    annualMetricResults.map(
      (result) =>
        result.data
          ?.reported_metrics
        ?? [],
    );

  const dashboards =
    dashboardResults.map(
      (result) =>
        result.data ?? null,
    );

  const snapshotMetrics =
    snapshotResult.data
      ?.reported_metrics
    ?? [];

  return (
    <div>
      <header>
        <p className="text-sm font-medium text-zinc-500">
          Senus PLC
        </p>

        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-zinc-950">
          Financials
        </h1>

        <p className="mt-2 text-sm text-zinc-500">
          Historical financial performance and derived metrics
        </p>
      </header>

      <section className="mt-8 overflow-hidden rounded-xl border border-zinc-200 bg-white shadow-sm">
        <div className="border-b border-zinc-200 px-6 py-4">
          <h2 className="font-semibold text-zinc-950">
            Income Statement
          </h2>

          <p className="mt-1 text-sm text-zinc-500">
            Reported values and backend-derived profitability metrics
          </p>
        </div>

        <FinancialTable
          annualMetrics={
            annualMetrics
          }
          dashboards={dashboards}
        />
      </section>

      <section className="mt-6 overflow-hidden rounded-xl border border-zinc-200 bg-white shadow-sm">
        <div className="border-b border-zinc-200 px-6 py-4">
          <h2 className="font-semibold text-zinc-950">
            Balance Sheet
          </h2>

          <p className="mt-1 text-sm text-zinc-500">
            Historical year-end position and latest available snapshot
          </p>
        </div>

        <BalanceSheetTable
          annualMetrics={
            annualMetrics
          }
          snapshotMetrics={
            snapshotMetrics
          }
          snapshotLabel={
            snapshotResult.data
              ?.period.label
            ?? "8 Dec 2025"
          }
        />
      </section>
    </div>
  );
}

function FinancialTable({
  annualMetrics,
  dashboards,
}: {
  annualMetrics: ReportedMetric[][];
  dashboards: Array<
    Awaited<
      ReturnType<
        typeof getDashboard
      >
    > | null
  >;
}) {
  const reportedValue = (
    periodIndex: number,
    metricCode: string,
  ) =>
    annualMetrics[
      periodIndex
    ].find(
      (metric) =>
        metric.metric
        === metricCode,
    )?.value ?? null;

  const dashboardValue = (
    periodIndex: number,
    metricCode:
      | "gross_margin"
      | "operating_margin"
      | "ebitda"
      | "ebitda_margin",
  ) => {
    const dashboard =
      dashboards[periodIndex];

    if (!dashboard) {
      return null;
    }

    return dashboard.kpis[
      metricCode
    ].value;
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-zinc-200 bg-zinc-50">
            <th className="px-6 py-3 text-left font-medium text-zinc-500">
              Metric
            </th>

            {annualPeriods.map(
              (period) => (
                <th
                  key={period.code}
                  className="px-6 py-3 text-right font-medium text-zinc-500"
                >
                  {period.label}
                </th>
              ),
            )}
          </tr>
        </thead>

        <tbody className="divide-y divide-zinc-100">
          <FinancialRow
            label="Revenue"
            values={annualPeriods.map(
              (_, index) =>
                currency(
                  reportedValue(
                    index,
                    "revenue",
                  ),
                ),
            )}
          />

          <FinancialRow
            label="Cost of Sales"
            values={annualPeriods.map(
              (_, index) =>
                currency(
                  reportedValue(
                    index,
                    "cost_of_sales",
                  ),
                ),
            )}
          />

          <FinancialRow
            label="Gross Profit"
            values={annualPeriods.map(
              (_, index) =>
                currency(
                  reportedValue(
                    index,
                    "gross_profit",
                  ),
                ),
            )}
            strong
          />

          <FinancialRow
            label="Gross Margin"
            values={annualPeriods.map(
              (_, index) =>
                percent(
                  dashboardValue(
                    index,
                    "gross_margin",
                  ),
                ),
            )}
          />

          <FinancialRow
            label="Administrative Expenses"
            values={annualPeriods.map(
              (_, index) =>
                currency(
                  reportedValue(
                    index,
                    "administrative_expenses",
                  ),
                ),
            )}
          />

          <FinancialRow
            label="Operating Profit / (Loss)"
            values={annualPeriods.map(
              (_, index) =>
                currency(
                  reportedValue(
                    index,
                    "operating_profit",
                  ),
                ),
            )}
            strong
          />

          <FinancialRow
            label="Operating Margin"
            values={annualPeriods.map(
              (_, index) =>
                percent(
                  dashboardValue(
                    index,
                    "operating_margin",
                  ),
                ),
            )}
          />

          <FinancialRow
            label="EBITDA"
            values={annualPeriods.map(
              (_, index) =>
                currency(
                  dashboardValue(
                    index,
                    "ebitda",
                  ),
                ),
            )}
            strong
          />

          <FinancialRow
            label="EBITDA Margin"
            values={annualPeriods.map(
              (_, index) =>
                percent(
                  dashboardValue(
                    index,
                    "ebitda_margin",
                  ),
                ),
            )}
          />

          <FinancialRow
            label="Net Income"
            values={annualPeriods.map(
              (_, index) =>
                currency(
                  reportedValue(
                    index,
                    "net_income",
                  ),
                ),
            )}
            strong
          />
        </tbody>
      </table>
    </div>
  );
}

function BalanceSheetTable({
  annualMetrics,
  snapshotMetrics,
  snapshotLabel,
}: {
  annualMetrics: ReportedMetric[][];
  snapshotMetrics: ReportedMetric[];
  snapshotLabel: string;
}) {
  const metricValue = (
    metrics: ReportedMetric[],
    metricCode: string,
  ) =>
    metrics.find(
      (metric) =>
        metric.metric
        === metricCode,
    )?.value ?? null;

  const columns = [
    {
      label: "30 Jun 2024",
      metrics:
        annualMetrics[0],
    },
    {
      label: "30 Jun 2025",
      metrics:
        annualMetrics[1],
    },
    {
      label: snapshotLabel,
      metrics:
        snapshotMetrics,
    },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-zinc-200 bg-zinc-50">
            <th className="px-6 py-3 text-left font-medium text-zinc-500">
              Metric
            </th>

            {columns.map(
              (column) => (
                <th
                  key={column.label}
                  className="px-6 py-3 text-right font-medium text-zinc-500"
                >
                  {column.label}
                </th>
              ),
            )}
          </tr>
        </thead>

        <tbody className="divide-y divide-zinc-100">
          <FinancialRow
            label="Cash"
            values={columns.map(
              (column) =>
                currency(
                  metricValue(
                    column.metrics,
                    "cash",
                  ),
                ),
            )}
          />

          <FinancialRow
            label="Debtors"
            values={columns.map(
              (column) =>
                currency(
                  metricValue(
                    column.metrics,
                    "debtors",
                  ),
                ),
            )}
          />

          <FinancialRow
            label="Current Assets"
            values={columns.map(
              (column) =>
                currency(
                  metricValue(
                    column.metrics,
                    "current_assets",
                  ),
                ),
            )}
            strong
          />

          <FinancialRow
            label="Current Liabilities"
            values={columns.map(
              (column) =>
                currency(
                  metricValue(
                    column.metrics,
                    "current_liabilities",
                  ),
                ),
            )}
          />

          <FinancialRow
            label="Long-term Liabilities"
            values={columns.map(
              (column) =>
                currency(
                  metricValue(
                    column.metrics,
                    "long_term_liabilities",
                  ),
                ),
            )}
          />

          <FinancialRow
            label="Net Assets"
            values={columns.map(
              (column) =>
                currency(
                  metricValue(
                    column.metrics,
                    "net_assets",
                  ),
                ),
            )}
            strong
          />
        </tbody>
      </table>
    </div>
  );
}

function currency(
  value: number | null,
) {
  return value === null
    ? "—"
    : formatCurrency(value);
}

function percent(
  value: number | null,
) {
  return value === null
    ? "—"
    : formatPercent(value);
}

function FinancialRow({
  label,
  values,
  strong = false,
}: {
  label: string;
  values: string[];
  strong?: boolean;
}) {
  return (
    <tr>
      <td
        className={`px-6 py-3 ${
          strong
            ? "font-semibold text-zinc-950"
            : "text-zinc-600"
        }`}
      >
        {label}
      </td>

      {values.map(
        (value, index) => (
          <td
            key={index}
            className={`px-6 py-3 text-right ${
              strong
                ? "font-semibold text-zinc-950"
                : "text-zinc-600"
            }`}
          >
            {value}
          </td>
        ),
      )}
    </tr>
  );
}