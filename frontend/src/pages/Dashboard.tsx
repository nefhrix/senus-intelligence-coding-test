import { useState } from "react";

import {
  useMutation,
  useQuery,
} from "@tanstack/react-query";

import KpiCard from "../components/dashboard/KpiCard";
import BalanceSheetSnapshot from "../components/dashboard/BalanceSheetSnapshot";

import RevenueChart from "../components/charts/RevenueChart";
import MarginChart from "../components/charts/MarginChart";
import LiquidityChart from "../components/charts/LiquidityChart";
import CashBurnChart from "../components/charts/CashBurnChart";

import {
  getDashboard,
} from "../api/dashboard";

import {
  generateBoardInsights,
} from "../api/ai";

import {
  formatCurrency,
  formatPercent,
} from "../utils/formatters";

const periods = [
  {
    id: "FY2025",
    label: "FY 2025",
  },
  {
    id: "FY2024",
    label: "FY 2024",
  },
];

export default function Dashboard() {
  const [
    selectedPeriodId,
    setSelectedPeriodId,
  ] = useState("FY2025");

  const {
    data,
    isLoading,
    isError,
  } = useQuery({
    queryKey: [
      "dashboard",
      selectedPeriodId,
    ],
    queryFn: () =>
      getDashboard(
        selectedPeriodId,
      ),
  });

  const aiMutation = useMutation({
    mutationFn: () =>
      generateBoardInsights(
        `
Give exactly 3 short Board-level insights.

Prioritise ${selectedPeriodId} where relevant.

Return exactly these three categories:

- Growth: one concise sentence
- Profitability: one concise sentence
- Liquidity: one concise sentence

Use only supplied financial data.

Do not add an introduction.
Do not add a conclusion.
Do not add headings.
Do not provide more than three bullet points.
        `.trim(),
      ),
  });

  if (isLoading) {
    return (
      <div className="flex min-h-96 items-center justify-center">
        <div className="h-7 w-7 animate-spin rounded-full border-2 border-zinc-200 border-t-zinc-950" />
      </div>
    );
  }

  if (
    isError ||
    !data
  ) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm font-medium text-red-700">
        Unable to load financial data.
      </div>
    );
  }

  const { kpis } = data;

  const currency = (
    value: number | null,
  ) =>
    value === null
      ? "—"
      : formatCurrency(
          value,
          true,
        );

  const percent = (
    value: number | null,
  ) =>
    value === null
      ? "—"
      : formatPercent(value);

  const multiple = (
    value: number | null,
  ) =>
    value === null
      ? "—"
      : `${value.toFixed(2)}x`;

  return (
    <div>
      <header className="flex items-center justify-between">
        <h1 className="text-3xl font-semibold tracking-tight text-zinc-950">
          Board Report
        </h1>

        <select
          value={
            selectedPeriodId
          }
          onChange={(event) => {
            setSelectedPeriodId(
              event.target.value,
            );

            aiMutation.reset();
          }}
          className="rounded-lg border border-zinc-300 bg-white px-4 py-2.5 text-sm font-medium text-zinc-800 outline-none transition focus:border-zinc-500"
        >
          {periods.map(
            (period) => (
              <option
                key={period.id}
                value={period.id}
              >
                {period.label}
              </option>
            ),
          )}
        </select>
      </header>

      <section className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <KpiCard
          label="Revenue"
          value={currency(
            kpis.revenue.value,
          )}
          change={
            kpis.revenue.change ==
            null
              ? undefined
              : kpis.revenue
                  .change * 100
          }
        />

        <KpiCard
          label="Gross Margin"
          value={percent(
            kpis.gross_margin
              .value,
          )}
        />

        <KpiCard
          label="EBITDA"
          value={currency(
            kpis.ebitda.value,
          )}
        />

        <KpiCard
          label="Operating Cash Flow"
          value={currency(
            kpis
              .operating_cash_flow
              .value,
          )}
        />

        <KpiCard
          label="Cash"
          value={currency(
            kpis.cash.value,
          )}
        />

        <KpiCard
          label="Current Ratio"
          value={multiple(
            kpis.current_ratio
              .value,
          )}
        />
      </section>

      <section className="mt-6 rounded-xl border border-zinc-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <h2 className="font-semibold text-zinc-950">
              Sena AI analysis  
            </h2>

          </div>

          <button
            type="button"
            onClick={() =>
              aiMutation.mutate()
            }
            disabled={
              aiMutation.isPending
            }
            className="rounded-lg bg-zinc-950 px-4 py-2 text-sm font-medium text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {aiMutation.isPending
              ? "Analysing..."
              : aiMutation.data
                ? "Refresh"
                : "Get Insights"}
          </button>
        </div>

        {aiMutation.isPending && (
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            {[1, 2, 3].map(
              (item) => (
                <div
                  key={item}
                  className="h-32 animate-pulse rounded-xl bg-zinc-100"
                />
              ),
            )}
          </div>
        )}

        {aiMutation.isError && (
          <div className="mt-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {aiMutation.error
              instanceof Error
              ? aiMutation.error
                  .message
              : "Unable to generate insights."}
          </div>
        )}

        {!aiMutation.isPending &&
          !aiMutation.isError &&
          !aiMutation.data && (
            <div className="mt-5 flex min-h-28 items-center justify-center rounded-xl bg-zinc-50">
              <p className="text-sm text-zinc-400">
                Generate a quick Board-level financial readout.
              </p>
            </div>
          )}

        {aiMutation.data && (
          <AiSnapshot
            text={
              aiMutation.data
                .insights
            }
          />
        )}
      </section>

      <section className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">
        <RevenueChart />

        <MarginChart />

        <LiquidityChart />

        <CashBurnChart />
      </section>

      <BalanceSheetSnapshot />
    </div>
  );
}

function AiSnapshot({
  text,
}: {
  text: string;
}) {
  const insights =
    parseAiInsights(text);

  return (
    <div className="mt-5 grid gap-3 md:grid-cols-3">
      {insights.map(
        (insight, index) => (
          <article
            key={`${insight.label}-${index}`}
            className="rounded-xl border border-zinc-200 bg-zinc-50 p-5"
          >
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
                {insight.label}
              </span>

              <span className="font-mono text-[10px] text-zinc-400">
                {String(
                  index + 1,
                ).padStart(
                  2,
                  "0",
                )}
              </span>
            </div>

            <p className="mt-4 text-sm leading-6 text-zinc-700">
              {insight.text}
            </p>
          </article>
        ),
      )}
    </div>
  );
}

function parseAiInsights(
  text: string,
) {
  const lines = text
    .split("\n")
    .map((line) =>
      line
        .trim()
        .replace(
          /^[-•]\s*/,
          "",
        )
        .replace(
          /\*\*/g,
          "",
        ),
    )
    .filter(Boolean);

  const fallbackLabels = [
    "Growth",
    "Profitability",
    "Liquidity",
  ];

  return lines
    .slice(0, 3)
    .map(
      (line, index) => {
        const match =
          line.match(
            /^(Growth|Profitability|Liquidity)\s*:\s*(.+)$/i,
          );

        if (match) {
          return {
            label:
              match[1],
            text:
              match[2],
          };
        }

        return {
          label:
            fallbackLabels[
              index
            ],
          text: line,
        };
      },
    );
}