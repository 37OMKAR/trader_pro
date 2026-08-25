import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#080b11",
        surface: "#0e131f",
        "surface-raised": "#151b2c",
        "surface-border": "#1e293b",
        "terminal-green": "#00ff9d",
        "terminal-red": "#ff3b5c",
        "terminal-cyan": "#00e5ff",
        "terminal-amber": "#ffb300",
        "terminal-purple": "#a855f7",
        "text-primary": "#f8fafc",
        "text-secondary": "#94a3b8",
        "text-muted": "#64748b",
      },
      fontFamily: {
        mono: ["var(--font-geist-mono)", "JetBrains Mono", "Courier New", "monospace"],
        sans: ["var(--font-geist-sans)", "Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        "glow-green": "0 0 15px rgba(0, 255, 157, 0.3)",
        "glow-red": "0 0 15px rgba(255, 59, 92, 0.3)",
        "glow-cyan": "0 0 15px rgba(0, 229, 255, 0.3)",
      },
    },
  },
  plugins: [],
} satisfies Config;
