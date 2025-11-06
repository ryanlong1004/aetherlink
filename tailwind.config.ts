import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        aether: {
          "deep-indigo": "#1a1a3e",
          indigo: "#2d2d5f",
          cyan: "#00e5ff",
          "cyan-glow": "#00ffff",
          brass: "#b8860b",
          bronze: "#cd7f32",
          "bronze-light": "#d4a574",
          dark: "#0a0a1a",
        },
      },
      fontFamily: {
        orbitron: ["Orbitron", "sans-serif"],
        merriweather: ["Merriweather", "serif"],
      },
      boxShadow: {
        "cyan-glow":
          "0 0 20px rgba(0, 229, 255, 0.3), 0 0 40px rgba(0, 229, 255, 0.1)",
        "bronze-glow":
          "0 0 20px rgba(205, 127, 50, 0.3), 0 0 40px rgba(205, 127, 50, 0.1)",
      },
    },
  },
  plugins: [],
} satisfies Config;
