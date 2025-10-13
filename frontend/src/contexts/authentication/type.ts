import type { AuthUser } from "aws-amplify/auth";

export type AuthenticationContextType = {
  logout: () => Promise<void>;
  user: AuthUser | null;
  authToken: string | null;
  idToken: string | null;
  fetchWithToken: (
    input: string | URL | Request,
    init?: RequestInit | undefined
  ) => Promise<Response>;
};
