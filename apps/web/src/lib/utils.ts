/**
 * Shared formatting helpers for the dashboard.
 */

/** Format a number as Indian Rupee currency, with optional compact Cr/L suffix. */
export function formatINR(
  value: number | null | undefined,
  compact: boolean | number = false,
  maximumFractionDigits = 2,
): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  // Back-compat: formatINR(value, 3) → treat 2nd arg as fraction digits
  if (typeof compact === "number") {
    maximumFractionDigits = compact;
    compact = false;
  }
  if (compact) {
    const abs = Math.abs(value);
    if (abs >= 1e7) return `₹ ${(value / 1e7).toFixed(2)} Cr`;
    if (abs >= 1e5) return `₹ ${(value / 1e5).toFixed(2)} L`;
    if (abs >= 1e3) return `₹ ${(value / 1e3).toFixed(2)} K`;
  }
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits,
  }).format(value);
}

/** Format a number with Indian-style grouping, no currency symbol. */
export function formatNumber(
  value: number | null | undefined,
  maximumFractionDigits = 2,
): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits,
    minimumFractionDigits: 0,
  }).format(value);
}

/** Format a decimal (e.g. 1.42 or 0.0142) as a percentage. Values >= 1 or <= -1 are treated as already-percent. */
export function formatPercent(
  value: number | null | undefined,
  maximumFractionDigits = 2,
): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const asPct = Math.abs(value) <= 1 ? value * 100 : value;
  const sign = asPct > 0 ? "+" : "";
  return `${sign}${asPct.toFixed(maximumFractionDigits)}%`;
}

/** Tiny classnames helper. */
export function cn(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(" ");
}
