/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Escala de magnitude — usada nos pins do mapa e badges
        magnitude: {
          safe: "#22c55e",      // verde — < 2.5
          low: "#eab308",       // amarelo — 2.5 a 5.0
          medium: "#f97316",    // laranja — 5.0 a 7.0
          high: "#ef4444",      // vermelho — > 7.0
          critical: "#7f1d1d",  // vermelho escuro — > 8.0
        },
      },
      animation: {
        "pulse-fast": "pulse 0.8s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "slide-in": "slideIn 0.3s ease-out",
      },
      keyframes: {
        slideIn: {
          "0%": { transform: "translateX(100%)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};
