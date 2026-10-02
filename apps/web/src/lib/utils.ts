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

/**
 * Format a value already expressed in percent (e.g. 1.42 → "+1.42%").
 *
 * The backend returns `percent_change` fields in percent units — the earlier
 * heuristic that rescaled values in [-1, 1] turned a real 0.91% move into a
 * fake "+91.00%". That heuristic is gone; callers that genuinely hold a
 * fraction should multiply by 100 themselves.
 */
export function formatPercent(
  value: number | null | undefined,
  maximumFractionDigits = 2,
): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(maximumFractionDigits)}%`;
}

/** Tiny classnames helper. */
export function cn(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(" ");
}
