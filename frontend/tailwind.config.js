/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: { 900: "#0a0c11", 800: "#11141b", 700: "#171a23", 600: "#1f2330" },
        accent: { DEFAULT: "#7c5cff", soft: "#5a4ad6", glow: "#9d83ff" },
        ink: { 50: "#f5f6fa", 200: "#c7cad6", 400: "#8c91a5", 600: "#5b6075" },
        success: "#22c55e", warn: "#f59e0b", danger: "#ef4444",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "Segoe UI", "sans-serif"],
        mono: ["JetBrains Mono", "Consolas", "monospace"],
      },
      boxShadow: {
        glow: "0 0 28px rgba(124, 92, 255, 0.35)",
      },
    },
  },
  plugins: [],
};
