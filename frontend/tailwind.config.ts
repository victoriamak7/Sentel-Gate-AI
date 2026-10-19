import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        sentinel: {
          dark: "#0b0f19",
          card: "#111827",
          border: "#1f2937",
          primary: "#3b82f6",
          accent: "#6366f1",
          safe: "#10b981",
          pii: "#f59e0b",
          blocked: "#ef4444",
          review: "#a855f7"
        }
      }
    },
  },
  plugins: [],
};
export default config;
