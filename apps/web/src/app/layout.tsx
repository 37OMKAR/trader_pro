import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Market AI — Indian Market Autonomous Intelligence & Paper-Trading Platform",
  description: "Institutional-grade AI intelligence platform for NSE, BSE, NIFTY 50, SENSEX, and Indian Derivatives.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen" style={{ background: "var(--paper)", color: "var(--ink)" }}>
        {children}
      </body>
    </html>
  );
}
