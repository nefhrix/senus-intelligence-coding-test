export function formatCurrency(
  value: number,
  compact = false
): string {
  return new Intl.NumberFormat("en-IE", {
    style: "currency",
    currency: "EUR",
    notation: compact ? "compact" : "standard",
    maximumFractionDigits: compact ? 1 : 0,
  }).format(value);
}

export function formatPercent(
  value: number | null,
  digits = 1
): string {
  if (value === null) return "—";

  return `${(value * 100).toFixed(digits)}%`;
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-IE").format(value);
}