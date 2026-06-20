import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const environment = loadEnv(mode, "..", "");
  const port = Number(process.env.VITE_PORT || environment.VITE_PORT || 5173);
  const backendUrl =
    process.env.VITE_BACKEND_URL ||
    environment.VITE_BACKEND_URL ||
    "http://127.0.0.1:8000";

  return {
    plugins: [react(), tailwindcss()],
    server: {
      port,
      strictPort: true,
      proxy: {
        "/api": {
          target: backendUrl,
          changeOrigin: true,
        },
        "/ws": {
          target: backendUrl.replace(/^http/, "ws"),
          changeOrigin: true,
          ws: true,
        },
      },
    },
  };
});
