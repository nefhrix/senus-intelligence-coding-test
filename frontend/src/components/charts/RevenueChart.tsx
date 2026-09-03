import { useQueries } from "@tanstack/react-query";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getDashboard } from "../../api/dashboard";
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


export default function RevenueChart() {
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
          Revenue Performance
        </h2>

        <div className="flex h-72 items-center justify-center text-sm text-zinc-400">
          Loading revenue data...
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h2 className="font-semibold text-zinc-950">
          Revenue Performance
        </h2>

        <div className="flex h-72 items-center justify-center text-sm text-red-500">
          Unable to load revenue data.
        </div>
      </div>
    );
  }

  const data = results.map(
    (result, index) => ({
      period: periods[index].label,
      revenue:
        result.data?.kpis.revenue.value ??
        0,
    }),
  );

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="font-semibold text-zinc-950">
          Revenue Performance
        </h2>

        <p className="mt-1 text-sm text-zinc-500">
          Reported revenue by financial year
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

            <Bar
              dataKey="revenue"
              name="Revenue"
              fill="#18181b"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}