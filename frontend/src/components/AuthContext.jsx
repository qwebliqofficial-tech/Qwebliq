import { createContext, useContext, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

import { api } from "@/lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const location = useLocation();
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const privateRoute = ["/login", "/admin", "/client"].includes(location.pathname);
    if (!privateRoute) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    api
      .get("/auth/me")
      .then((response) => setUser(response.data))
      .catch(() => setUser(null))
      .finally(() => setIsLoading(false));
  }, [location.pathname]);

  const value = {
    user,
    isLoading,
    setUser,
    logout: async () => {
      await api.post("/auth/logout");
      setUser(null);
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}