/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts}"],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#0a0e1a",
          secondary: "#121826",
          tertiary: "#1a2133",
          elevated: "#1e2640",
        },
        neon: {
          cyan: "#00f0ff",
          green: "#00ff88",
        },
        sev: {
          critical: "#ff3366",
          high: "#ff6644",
          medium: "#ffaa00",
          low: "#4a9eff",
          info: "#6b7d99",
        },
        txt: {
          primary: "#e0e6ed",
          secondary: "#8b95a7",
          tertiary: "#5a6577",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      backdropBlur: {
        glass: "12px",
      },
    },
  },
  plugins: [],
};
