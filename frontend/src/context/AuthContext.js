import {
  createContext,
  useContext,
  useState,
  useEffect,
} from "react";

import { authAPI } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {

  const [user, setUser] =
    useState(null);

  const [loading, setLoading] =
    useState(true);


  useEffect(() => {

    authAPI
      .me()

      .then((r) => {
        setUser(r.data);
      })

      .catch(() => {
        setUser(null);
      })

      .finally(() => {
        setLoading(false);
      });

  }, []);


  const login = async (
    credentials
  ) => {

    const r =
      await authAPI.login(
        credentials
      );

    // Save JWT token
    localStorage.setItem(
      "token",
      r.data.token
    );

    setUser(r.data.user);

    return r.data;
  };


  const logout = async () => {

    await authAPI.logout();

    localStorage.removeItem(
      "token"
    );

    setUser(null);
  };


  const register = async (
    data
  ) => {

    const r =
      await authAPI.register(
        data
      );

    return r.data;
  };


  return (

    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        register,
      }}
    >

      {children}

    </AuthContext.Provider>
  );
}


export const useAuth = () =>
  useContext(AuthContext);