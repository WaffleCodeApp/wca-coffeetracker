export const apiConfig = {
  my_container: {
    protocol: "https://",
    host: import.meta.env.VITE_HTTP_API_V2_HOST,
    path: "/my_container",
  },
  region: import.meta.env.VITE_AWS_PROJECT_REGION,
};


