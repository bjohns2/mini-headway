import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Vite 7 blocks requests from non-allowlisted hosts. The leading "." is
    // a subdomain wildcard so any preview URL CodeSignal hands out works.
    allowedHosts: [".codesignalusercontent.com"],
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
