import { useQueries } from "@tanstack/react-query";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getDashboard } from "../../api/dashboard";


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


export default function MarginChart() {
  const results = useQueries({
    queries: periods.map((period) => ({
      queryKey: [
        "dashboard",
        period.code,
      ],
      queryFn: () =>
        getDashboard(period.code),
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
          Margin Performance
        </h2>

        <div className="flex h-72 items-center justify-center text-sm text-zinc-400">
          Loading margin data...
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h2 className="font-semibold text-zinc-950">
          Margin Performance
        </h2>

        <div className="flex h-72 items-center justify-center text-sm text-red-500">
          Unable to load margin data.
        </div>
      </div>
    );
  }

  const data = results.map(
    (result, index) => ({
      period: periods[index].label,
      grossMargin:
        (
          result.data?.kpis
            .gross_margin.value
          ?? 0
        ) * 100,
      ebitdaMargin:
        (
          result.data?.kpis
            .ebitda_margin.value
          ?? 0
        ) * 100,
    }),
  );

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="font-semibold text-zinc-950">
          Margin Performance
        </h2>

        <p className="mt-1 text-sm text-zinc-500">
          Gross margin and EBITDA margin
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
                `${Number(value).toFixed(0)}%`
              }
              tickLine={false}
              axisLine={false}
            />

            <Tooltip
              formatter={(value) =>
                `${Number(value).toFixed(1)}%`
              }
            />

            <Legend />

            <ReferenceLine
              y={0}
              stroke="#71717a"
              strokeDasharray="4 4"
            />

            <Line
              type="monotone"
              dataKey="grossMargin"
              name="Gross Margin"
              stroke="#18181b"
              strokeWidth={2}
            />

            <Line
              type="monotone"
              dataKey="ebitdaMargin"
              name="EBITDA Margin"
              stroke="#71717a"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}