export const userPoolId = import.meta.env.VITE_AWS_USER_POOL_ID || "";
export const region = import.meta.env.VITE_AWS_COGNITO_REGION || "";
export const userPoolClientId =
  import.meta.env.VITE_AWS_USER_POOL_CLIENT_ID || "";
export const cognitoDomain =
  import.meta.env.VITE_AWS_COGNITO_DOMAIN ||
  import.meta.env.VITE_COGNITO_DOMAIN ||
  "";

export const cognitoIdentityPoolId =
  import.meta.env.VITE_AWS_COGNITO_IDENTITY_POOL_ID || "";
