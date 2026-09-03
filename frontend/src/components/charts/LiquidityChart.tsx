import { useQueries, useQuery } from "@tanstack/react-query";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  getDashboard,
  getReportedMetrics,
} from "../../api/dashboard";
import { formatCurrency } from "../../utils/formatters";


const annualPeriods = [
  {
    code: "FY2024",
    label: "Jun 2024",
  },
  {
    code: "FY2025",
    label: "Jun 2025",
  },
];


export default function LiquidityChart() {
  const annualResults = useQueries({
    queries: annualPeriods.map((period) => ({
      queryKey: [
        "dashboard",
        period.code,
      ],
      queryFn: () =>
        getDashboard(period.code),
    })),
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
    annualResults.some(
      (result) => result.isLoading,
    )
    || snapshotResult.isLoading;

  const isError =
    annualResults.some(
      (result) => result.isError,
    )
    || snapshotResult.isError;

  if (isLoading) {
    return (
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h2 className="font-semibold text-zinc-950">
          Cash & Liquidity
        </h2>

        <div className="flex h-72 items-center justify-center text-sm text-zinc-400">
          Loading liquidity data...
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h2 className="font-semibold text-zinc-950">
          Cash & Liquidity
        </h2>

        <div className="flex h-72 items-center justify-center text-sm text-red-500">
          Unable to load liquidity data.
        </div>
      </div>
    );
  }

const snapshotCash =
  snapshotResult.data?.reported_metrics.find(
    (metric) =>
      metric.metric === "cash",
  )?.value ?? 0;

  const data = [
    {
      period: "Jun 2024",
      cash:
        annualResults[0].data
          ?.kpis.cash.value
        ?? 0,
    },
    {
      period: "Jun 2025",
      cash:
        annualResults[1].data
          ?.kpis.cash.value
        ?? 0,
    },
    {
      period: "Dec 2025",
      cash: snapshotCash,
    },
  ];

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="font-semibold text-zinc-950">
          Cash & Liquidity
        </h2>

        <p className="mt-1 text-sm text-zinc-500">
          Period-end cash position
        </p>
      </div>

      <div className="mt-6 h-72">
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <LineChart data={data}>
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

            <Line
              type="monotone"
              dataKey="cash"
              name="Cash"
              stroke="#18181b"
              strokeWidth={3}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}