// vite.config.ts
import path from "path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";
import TanStackRouterVite from "@tanstack/router-plugin/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tsconfigPaths(),
    TanStackRouterVite(), // ← NUEVO: Genera routeTree.gen.ts automáticamente
    react(),
    tailwindcss(),
  ],
  resolve: {
    // Resolve common extensions and add an explicit alias for the `@/lib` path
    // so imports like "@/lib/store/AuthStore" resolve correctly on case-sensitive CI.
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@/lib": path.resolve(__dirname, "./src/lib"),
    },
    extensions: [".mjs", ".js", ".ts", ".tsx", ".jsx", ".json"],
  },
  build: {
    outDir: "dist",
  },
});
