import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Allow external connections
    port: 5173,
    watch: {
      usePolling: false, // Use native file system events
    },
  },
  build: {
    // Reduce verbosity for CI/CD
    reportCompressedSize: false,
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
        },
      },
    },
  },
  define: {
    // Polyfill for amazon-cognito-identity-js
    global: "globalThis",
    // Define environment variables that should be available in the client
    "import.meta.env.VITE_HTTP_API_V2_HOST": JSON.stringify(
      process.env.VITE_HTTP_API_V2_HOST
    ),
    "import.meta.env.VITE_DEPLOYMENT_DOMAIN_NAME": JSON.stringify(
      process.env.VITE_DEPLOYMENT_DOMAIN_NAME
    ),
    "import.meta.env.VITE_PIPELINE_ID": JSON.stringify(
      process.env.VITE_PIPELINE_ID
    ),
    "import.meta.env.VITE_AWS_PROJECT_REGION": JSON.stringify(
      process.env.VITE_AWS_PROJECT_REGION
    ),
    // Cognito environment variables
    "import.meta.env.VITE_AWS_USER_POOL_ID": JSON.stringify(
      process.env.VITE_AWS_USER_POOL_ID
    ),
    "import.meta.env.VITE_AWS_COGNITO_REGION": JSON.stringify(
      process.env.VITE_AWS_COGNITO_REGION
    ),
    "import.meta.env.VITE_AWS_USER_POOL_CLIENT_ID": JSON.stringify(
      process.env.VITE_AWS_USER_POOL_CLIENT_ID
    ),
    "import.meta.env.VITE_COGNITO_DOMAIN": JSON.stringify(
      process.env.VITE_COGNITO_DOMAIN
    ),
    "import.meta.env.VITE_AWS_COGNITO_IDENTITY_POOL_ID": JSON.stringify(
      process.env.VITE_AWS_COGNITO_IDENTITY_POOL_ID
    ),
  },
});
