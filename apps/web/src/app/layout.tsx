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
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen bg-[#06090e] text-slate-100 selection:bg-cyan-500 selection:text-black">
        {children}
      </body>
    </html>
  );
}
