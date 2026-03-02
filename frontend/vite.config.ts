import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  server: {
    host: "0.0.0.0",   // necessário para expor dentro do Docker
    port: 5173,
    proxy: {
      // Redireciona /api/* para o backend — evita CORS em desenvolvimento
      "/api": {
        target: "http://api:8000",
        changeOrigin: true,
      },
      // Redireciona WebSocket
      "/ws": {
        target: "ws://api:8000",
        ws: true,
        changeOrigin: true,
      },
    },
  },

  // Otimizações de build para produção
  build: {
    target: "esnext",
    minify: "esbuild",
    rollupOptions: {
      output: {
        // Code splitting: separa bibliotecas grandes em chunks distintos
        // Melhora o tempo de carregamento (o usuário baixa só o que precisa)
        manualChunks: {
          "react-vendor": ["react", "react-dom"],
          "map-vendor": ["leaflet", "react-leaflet"],
          "chart-vendor": ["recharts"],
        },
      },
    },
  },
});
