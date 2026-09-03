type KpiCardProps = {
  label: string;
  value: string;
  change?: number;
  subtitle?: string;
};

export default function KpiCard({
  label,
  value,
  change,
  subtitle,
}: KpiCardProps) {
  const positive = change !== undefined && change >= 0;

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-zinc-500">
        {label}
      </p>

      <div className="mt-2 flex items-end justify-between">
        <p className="text-2xl font-semibold tracking-tight text-zinc-950">
          {value}
        </p>

        {change !== undefined && (
          <span
            className={
              positive
                ? "text-sm font-medium text-emerald-600"
                : "text-sm font-medium text-red-600"
            }
          >
            {positive ? "+" : ""}
            {change.toFixed(1)}%
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-2 text-xs text-zinc-400">
          {subtitle}
        </p>
      )}
    </div>
  );
}