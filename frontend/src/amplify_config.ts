import { Amplify } from "aws-amplify";
import type { ResourcesConfig } from "aws-amplify";

// Get environment variables
const userPoolId = import.meta.env.VITE_AWS_USER_POOL_ID || "";
const userPoolClientId = import.meta.env.VITE_AWS_USER_POOL_CLIENT_ID || "";
const cognitoDomain = import.meta.env.VITE_AWS_COGNITO_DOMAIN || "";
const region = import.meta.env.VITE_AWS_COGNITO_REGION || "";

// Configure Amplify at app level - runs before any components mount
export const configureAmplify = () => {
  console.log("Configuring Amplify at app level:", {
    userPoolId,
    userPoolClientId,
    cognitoDomain,
    region,
  });

  if (!userPoolId || !userPoolClientId) {
    console.error("Missing required Cognito configuration");
    return false;
  }

  const amplifyConfig: ResourcesConfig = {
    Auth: {
      Cognito: {
        userPoolId,
        userPoolClientId,
      },
    },
  };

  // Add realtime endpoint if available (TypeScript workaround for missing type)
  Amplify.configure(amplifyConfig);
  console.log("Amplify configured successfully at app level");

  return true;
};

// Export configuration status
export const isAmplifyConfigured = configureAmplify();
