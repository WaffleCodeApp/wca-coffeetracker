import { useEffect, useState, type ReactNode } from "react";
import { getCurrentUser, signInWithRedirect } from "aws-amplify/auth";
import { Hub } from "aws-amplify/utils";

export const AuthCheck = (props: {
  loading: ReactNode;
  authenticated: ReactNode;
}) => {
  const { loading, authenticated } = props;
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication status
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        setIsLoading(true);
        await getCurrentUser();
        setIsAuthenticated(true);
        console.log("User authenticated successfully");
      } catch {
        console.log("User not authenticated, redirecting to Cognito hosted UI");
        setIsAuthenticated(false);

        // Redirect to Cognito hosted UI for authentication
        try {
          await signInWithRedirect();
        } catch (signInError) {
          console.error("Sign in redirect failed:", signInError);
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  // Listen for auth state changes
  useEffect(() => {
    const hubListener = Hub.listen("auth", ({ payload }) => {
      switch (payload.event) {
        case "signedIn":
          console.log("User signed in successfully");
          setIsAuthenticated(true);
          break;
        case "signedOut":
          console.log("User signed out");
          setIsAuthenticated(false);
          break;
        case "tokenRefresh":
          console.log("Token refreshed successfully");
          break;
        case "tokenRefresh_failure":
          console.error("Token refresh failed:", payload.data);
          break;
        default:
          break;
      }
    });

    return () => hubListener();
  }, []);

  if (isLoading) {
    return loading;
  }

  if (!isAuthenticated) {
    return <div>Redirecting to login...</div>;
  }

  return authenticated;
};
