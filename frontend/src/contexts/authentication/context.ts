import { createContext } from "react";
import type { AuthenticationContextType } from "./type";

export const AuthenticationContext = createContext<AuthenticationContextType>({
  logout: async () => {},
  user: null,
  authToken: null,
  idToken: null,
  fetchWithToken: async () => new Response(),
});
