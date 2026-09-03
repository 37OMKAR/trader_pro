export function formatINR(value: number | null | undefined, compact = false): string {
  if (value === null || value === undefined || isNaN(Number(value))) return "₹—";
  const n = Number(value);
  if (compact) {
    const abs = Math.abs(n);
    if (abs >= 1e7) return `${n < 0 ? "-" : ""}₹${(abs / 1e7).toFixed(2)} Cr`;
    if (abs >= 1e5) return `${n < 0 ? "-" : ""}₹${(abs / 1e5).toFixed(2)} L`;
    if (abs >= 1e3) return `${n < 0 ? "-" : ""}₹${(abs / 1e3).toFixed(2)} K`;
  }
  return `₹${n.toLocaleString("en-IN", { maximumFractionDigits: 2 })}`;
}

export function formatNumber(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || isNaN(Number(value))) return "—";
  return Number(value).toLocaleString("en-IN", { maximumFractionDigits: digits });
}

export function formatPercent(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || isNaN(Number(value))) return "—";
  const n = Number(value);
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(digits)}%`;
}
