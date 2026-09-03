import { useQueries } from "@tanstack/react-query";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getReportedMetrics } from "../../api/dashboard";
import { formatCurrency } from "../../utils/formatters";

const periods = [
  {
    code: "FY2024",
    label: "FY 2024",
  },
  {
    code: "FY2025",
    label: "FY 2025",
  },
];

export default function CashBurnChart() {
  const results = useQueries({
    queries: periods.map((period) => ({
      queryKey: [
        "reported-metrics",
        period.code,
      ],
      queryFn: () =>
        getReportedMetrics(period.code),
    })),
  });

  const isLoading = results.some(
    (result) => result.isLoading,
  );

  const isError = results.some(
    (result) => result.isError,
  );

  if (isLoading) {
    return (
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h2 className="font-semibold text-zinc-950">
          Loss & Cash Burn
        </h2>

        <div className="flex h-72 items-center justify-center text-sm text-zinc-400">
          Loading cash burn data...
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h2 className="font-semibold text-zinc-950">
          Loss & Cash Burn
        </h2>

        <div className="flex h-72 items-center justify-center text-sm text-red-500">
          Unable to load cash burn data.
        </div>
      </div>
    );
  }

  const data = results.map(
    (result, index) => {
      const metrics =
        result.data?.reported_metrics ?? [];

      const operatingProfit =
        metrics.find(
          (metric) =>
            metric.metric
            === "operating_profit",
        )?.value ?? null;

      const operatingCashFlow =
        metrics.find(
          (metric) =>
            metric.metric
            === "operating_cash_flow",
        )?.value ?? null;

      return {
        period: periods[index].label,
        operatingProfit,
        operatingCashFlow,
      };
    },
  );

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="font-semibold text-zinc-950">
          Loss & Cash Burn
        </h2>

        <p className="mt-1 text-sm text-zinc-500">
          Operating result versus operating cash flow
        </p>
      </div>

      <div className="mt-6 h-72">
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <BarChart data={data}>
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey="period"
              tickLine={false}
              axisLine={false}
            />

            <YAxis
              tickFormatter={(value) =>
                formatCurrency(
                  Number(value),
                  true,
                )
              }
              tickLine={false}
              axisLine={false}
            />

            <Tooltip
              formatter={(value) =>
                formatCurrency(
                  Number(value),
                )
              }
            />

            <Legend />

            <ReferenceLine
              y={0}
              stroke="#71717a"
            />

            <Bar
              dataKey="operatingProfit"
              name="Operating Result"
              fill="#18181b"
              radius={[4, 4, 0, 0]}
            />

            <Bar
              dataKey="operatingCashFlow"
              name="Operating Cash Flow"
              fill="#a1a1aa"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}