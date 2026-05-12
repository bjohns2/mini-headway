import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Vite 7 blocks requests from non-allowlisted hosts. Leading "." is a
    // subdomain wildcard. github.dev covers GitHub Codespaces forwarded ports;
    // codesignalusercontent.com covers the CodeSignal interview preview.
    allowedHosts: [".app.github.dev", ".codesignalusercontent.com"],
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
