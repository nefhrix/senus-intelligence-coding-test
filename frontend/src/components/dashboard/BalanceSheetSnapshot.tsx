import { useQuery } from "@tanstack/react-query";

import { getReportedMetrics } from "../../api/dashboard";
import { formatCurrency } from "../../utils/formatters";

export default function BalanceSheetSnapshot() {
  const {
    data,
    isLoading,
    isError,
  } = useQuery({
    queryKey: [
      "reported-metrics",
      "BS_2025_12_08",
    ],
    queryFn: () =>
      getReportedMetrics(
        "BS_2025_12_08",
      ),
  });

  if (isLoading) {
    return (
      <section className="mt-6 rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="flex min-h-32 items-center justify-center text-sm text-zinc-400">
          Loading latest balance sheet...
        </div>
      </section>
    );
  }

  if (
    isError
    || !data
  ) {
    return (
      <section className="mt-6 rounded-xl border border-red-200 bg-red-50 p-6">
        <p className="text-sm font-medium text-red-700">
          Unable to load the latest balance sheet.
        </p>
      </section>
    );
  }

  const getMetric = (
    metricCode: string,
  ) =>
    data.reported_metrics.find(
      (metric) =>
        metric.metric === metricCode,
    )?.value ?? null;

  const cash = getMetric("cash");
  const currentAssets = getMetric(
    "current_assets",
  );
  const currentLiabilities = getMetric(
    "current_liabilities",
  );
  const netAssets = getMetric(
    "net_assets",
  );

  const currency = (
    value: number | null,
  ) =>
    value === null
      ? "—"
      : formatCurrency(
          value,
          true,
        );

  return (
    <section className="mt-6 rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="font-semibold text-zinc-950">
            Latest Balance Sheet Snapshot
          </h2>

          <p className="mt-1 text-sm text-zinc-500">
            As at {data.period.label}
          </p>
        </div>

        <span className="rounded-full bg-zinc-100 px-3 py-1 text-xs font-medium text-zinc-600">
          Latest available
        </span>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric
          label="Cash"
          value={currency(cash)}
        />

        <Metric
          label="Current Assets"
          value={currency(
            currentAssets,
          )}
        />

        <Metric
          label="Current Liabilities"
          value={currency(
            currentLiabilities,
          )}
        />

        <Metric
          label="Net Assets"
          value={currency(
            netAssets,
          )}
        />
      </div>
    </section>
  );
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg bg-zinc-50 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
        {label}
      </p>

      <p className="mt-2 text-xl font-semibold text-zinc-950">
        {value}
      </p>
    </div>
  );
}