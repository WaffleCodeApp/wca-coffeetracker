import { useState, useCallback, useEffect } from "react";
import {
  signOut,
  getCurrentUser,
  fetchAuthSession,
  type AuthUser,
} from "aws-amplify/auth";
import { Hub } from "aws-amplify/utils";
import { AuthenticationContext } from "./context";

// Amplify is now configured at app level before any components mount

const AuthenticationProviderInner = (props: { children: React.ReactNode }) => {
  const { children } = props;

  const [user, setUser] = useState<AuthUser | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [idToken, setIdToken] = useState<string | null>(null);

  // Initialize user state from Amplify
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const currentUser = await getCurrentUser();
        const session = await fetchAuthSession();

        setUser(currentUser);
        setAuthToken(session.tokens?.accessToken?.toString() || null);
        setIdToken(session.tokens?.idToken?.toString() || null);

        console.log("Amplify authentication initialized:", {
          userId: currentUser.userId,
          username: currentUser.username,
          hasAccessToken: !!session.tokens?.accessToken,
          hasIdToken: !!session.tokens?.idToken,
        });
      } catch (error) {
        console.log("No authenticated user found:", error);
        setUser(null);
        setAuthToken(null);
        setIdToken(null);
      }
    };

    initializeAuth();

    // Listen for auth state changes
    const hubListener = Hub.listen("auth", ({ payload }) => {
      switch (payload.event) {
        case "signedIn":
          console.log("User signed in, updating auth state");
          initializeAuth();
          break;
        case "signedOut":
          console.log("User signed out, clearing auth state");
          setUser(null);
          setAuthToken(null);
          setIdToken(null);
          localStorage.removeItem("selectedOrganizationId");
          break;
        case "tokenRefresh":
          console.log("Token refreshed, updating auth state");
          initializeAuth();
          break;
        default:
          break;
      }
    });

    return () => hubListener();
  }, []);

  const logout = async () => {
    try {
      await signOut();
      setUser(null);
      setAuthToken(null);
      setIdToken(null);

      // Clear localStorage
      localStorage.removeItem("selectedOrganizationId");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const jwtFetch = useCallback(
    async (input: string | URL | Request, init?: RequestInit | undefined) => {
      if (!authToken) {
        throw new Error("No access token found");
      }

      // Prepare headers with JWT authentication
      const headers: Record<string, string> = {
        'Authorization': `Bearer ${authToken}`,
      };

      // Add existing headers from init
      if (init?.headers) {
        if (init.headers instanceof Headers) {
          init.headers.forEach((value, key) => {
            headers[key] = value;
          });
        } else if (Array.isArray(init.headers)) {
          init.headers.forEach(([key, value]) => {
            headers[key] = value;
          });
        } else {
          Object.entries(init.headers).forEach(([key, value]) => {
            headers[key] = value;
          });
        }
      }

      // Add idToken to custom header if available
      if (idToken) {
        headers['X-IdToken'] = idToken;
      }

      return fetch(input, {
        ...init,
        headers,
      });
    },
    [authToken, idToken]
  );

  return (
    <AuthenticationContext.Provider
      value={{
        logout,
        user,
        authToken,
        idToken,
        fetchWithToken: jwtFetch,
      }}
    >
      {children}
    </AuthenticationContext.Provider>
  );
};

export const AuthenticationProvider = (props: {
  children: React.ReactNode;
}) => {
  const { children } = props;

  // Environment validation is now handled at app level

  return (
    <AuthenticationProviderInner>{children}</AuthenticationProviderInner>
  );
};
