// Types for infrastructure config
type Service = 
  | { stackType: "FUNCTION"; functionTrigger?: "HTTP_API_TRIGGER" | "HTTP_API_QUEUE_TRIGGER" | "QUEUE_TRIGGER" }
  | { stackType: "CONTAINER"; integration?: "API_GATEWAY" | "ALB" };

type Resources = {
  envFeatures: {
    httpApiV2?: { enabled?: boolean; subdomain?: string };
    restApiV1?: { enabled?: boolean; subdomain?: string };
  };
  services: Record<string, Service>;
};

interface ConnectionConfig {
  host: string;
  path: string;
}

function determineConnectionConfig(): ConnectionConfig {
  console.log("🔍 [api_config] Starting connection config determination");
  
  const buildEnvVarsJson = import.meta.env.VITE_BUILD_ENV_VARS_JSON;
  const deploymentDomainName = import.meta.env.VITE_DEPLOYMENT_DOMAIN_NAME;
  const httpApiV2Host = import.meta.env.VITE_HTTP_API_V2_HOST;

  console.log("📥 [api_config] Environment variables received:", {
    hasVITE_BUILD_ENV_VARS_JSON: !!buildEnvVarsJson,
    VITE_BUILD_ENV_VARS_JSON_length: buildEnvVarsJson?.length || 0,
    VITE_BUILD_ENV_VARS_JSON_preview: buildEnvVarsJson ? buildEnvVarsJson.substring(0, 200) + (buildEnvVarsJson.length > 200 ? "..." : "") : "undefined",
    hasVITE_DEPLOYMENT_DOMAIN_NAME: !!deploymentDomainName,
    VITE_DEPLOYMENT_DOMAIN_NAME: deploymentDomainName || "undefined",
    hasVITE_HTTP_API_V2_HOST: !!httpApiV2Host,
    VITE_HTTP_API_V2_HOST: httpApiV2Host || "undefined",
  });

  if (!buildEnvVarsJson || !deploymentDomainName) {
    console.warn("⚠️ [api_config] Missing required environment variables, using fallback");
    const fallback = {
      host: httpApiV2Host || "",
      path: "/api/hello_world",
    };
    console.log("🔄 [api_config] Fallback config:", fallback);
    return fallback;
  }

  try {
    console.log("📦 [api_config] Parsing VITE_BUILD_ENV_VARS_JSON...");
    // The JSON has the structure of resourcesSchema directly (envFeatures and services at top level)
    const config: Resources = JSON.parse(buildEnvVarsJson);
    const { envFeatures, services } = config;
    
    console.log("✅ [api_config] Successfully parsed config:", {
      envFeatures: {
        httpApiV2: envFeatures.httpApiV2,
        restApiV1: envFeatures.restApiV1,
      },
      services_count: Object.keys(services).length,
      service_names: Object.keys(services),
      services_detail: Object.entries(services).map(([name, service]) => {
        const base = { name, stackType: service.stackType };
        if (service.stackType === "FUNCTION") {
          return { ...base, functionTrigger: service.functionTrigger };
        }
        if (service.stackType === "CONTAINER") {
          return { ...base, integration: service.integration };
        }
        return base;
      }),
    });

    // Find the first service that matches our criteria
    const findServiceName = (predicate: (service: Service) => boolean, searchType: string): string | null => {
      console.log(`🔎 [api_config] Searching for service with criteria: ${searchType}`);
      for (const [serviceName, service] of Object.entries(services)) {
        const matches = predicate(service);
        const serviceInfo = (() => {
          const base = { stackType: service.stackType, matches };
          if (service.stackType === "FUNCTION") {
            return { ...base, functionTrigger: service.functionTrigger };
          }
          if (service.stackType === "CONTAINER") {
            return { ...base, integration: service.integration };
          }
          return base;
        })();
        console.log(`  - Checking service "${serviceName}":`, serviceInfo);
        if (matches) {
          console.log(`  ✅ Found matching service: "${serviceName}"`);
          return serviceName;
        }
      }
      console.log(`  ❌ No matching service found for: ${searchType}`);
      return null;
    };

    // Check for HTTP API V2
    console.log("🌐 [api_config] Checking HTTP API V2 configuration...");
    if (envFeatures.httpApiV2?.enabled) {
      console.log("  ✅ HTTP API V2 is enabled");
      const subdomain = envFeatures.httpApiV2.subdomain || "api";
      console.log(`  📍 Using subdomain: "${subdomain}"`);
      
      const serviceName = findServiceName((service) => {
        if (service.stackType === "FUNCTION") {
          return service.functionTrigger === "HTTP_API_TRIGGER" || 
                 service.functionTrigger === "HTTP_API_QUEUE_TRIGGER";
        }
        if (service.stackType === "CONTAINER") {
          return service.integration === "API_GATEWAY";
        }
        return false;
      }, "HTTP_API_V2 (FUNCTION with HTTP_API_TRIGGER/HTTP_API_QUEUE_TRIGGER or CONTAINER with API_GATEWAY)");

      if (serviceName) {
        const config = {
          host: `${subdomain}.${deploymentDomainName}`,
          path: `/${serviceName}/hello_world`,
        };
        console.log("✅ [api_config] Using HTTP API V2 configuration:", config);
        console.log("🔗 [api_config] Full URL will be:", `https://${config.host}${config.path}`);
        return config;
      } else {
        console.log("  ⚠️ HTTP API V2 enabled but no matching service found");
      }
    } else {
      console.log("  ❌ HTTP API V2 is not enabled");
    }

    // Check for REST API V1
    console.log("🌐 [api_config] Checking REST API V1 configuration...");
    if (envFeatures.restApiV1?.enabled) {
      console.log("  ✅ REST API V1 is enabled");
      const subdomain = envFeatures.restApiV1.subdomain || "api";
      console.log(`  📍 Using subdomain: "${subdomain}"`);
      
      const serviceName = findServiceName((service) => {
        if (service.stackType === "FUNCTION") {
          return service.functionTrigger === "HTTP_API_TRIGGER" || 
                 service.functionTrigger === "HTTP_API_QUEUE_TRIGGER";
        }
        if (service.stackType === "CONTAINER") {
          return service.integration === "API_GATEWAY";
        }
        return false;
      }, "REST_API_V1 (FUNCTION with HTTP_API_TRIGGER/HTTP_API_QUEUE_TRIGGER or CONTAINER with API_GATEWAY)");

      if (serviceName) {
        const config = {
          host: `${subdomain}.${deploymentDomainName}`,
          path: `/${serviceName}/hello_world`,
        };
        console.log("✅ [api_config] Using REST API V1 configuration:", config);
        console.log("🔗 [api_config] Full URL will be:", `https://${config.host}${config.path}`);
        return config;
      } else {
        console.log("  ⚠️ REST API V1 enabled but no matching service found");
      }
    } else {
      console.log("  ❌ REST API V1 is not enabled");
    }

    // Fallback to ALB integration
    console.log("🌐 [api_config] Checking ALB integration (fallback)...");
    const albServiceName = findServiceName((service) => {
      return service.stackType === "CONTAINER" && service.integration === "ALB";
    }, "ALB (CONTAINER with ALB integration)");

    if (albServiceName) {
      const config = {
        host: `${albServiceName}.${deploymentDomainName}`,
        path: "/hello_world",
      };
      console.log("✅ [api_config] Using ALB integration configuration:", config);
      console.log("🔗 [api_config] Full URL will be:", `https://${config.host}${config.path}`);
      return config;
    } else {
      console.log("  ❌ No ALB service found");
    }

    // Final fallback
    console.warn("⚠️ [api_config] No matching configuration found, using final fallback");
    const fallback = {
      host: httpApiV2Host || "",
      path: "/api/hello_world",
    };
    console.log("🔄 [api_config] Final fallback config:", fallback);
    console.log("🔗 [api_config] Full URL will be:", `https://${fallback.host}${fallback.path}`);
    return fallback;
  } catch (error) {
    console.error("❌ [api_config] Failed to parse VITE_BUILD_ENV_VARS_JSON:", error);
    if (error instanceof Error) {
      console.error("  Error message:", error.message);
      console.error("  Error stack:", error.stack);
    }
    const fallback = {
      host: httpApiV2Host || "",
      path: "/api/hello_world",
    };
    console.log("🔄 [api_config] Error fallback config:", fallback);
    console.log("🔗 [api_config] Full URL will be:", `https://${fallback.host}${fallback.path}`);
    return fallback;
  }
}

const connectionConfig = determineConnectionConfig();

export const apiConfig = {
  aBackendService: {
    protocol: "https://",
    host: connectionConfig.host,
    path: connectionConfig.path,
  },
};

// Log the final apiConfig
console.log("🎯 [api_config] Final apiConfig:", apiConfig);
console.log("🔗 [api_config] Final constructed URL:", `${apiConfig.aBackendService.protocol}${apiConfig.aBackendService.host}${apiConfig.aBackendService.path}`);


