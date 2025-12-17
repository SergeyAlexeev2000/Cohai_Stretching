// src/context/AuthContext.jsx
import React, {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => {
    return localStorage.getItem("auth_token") || null;
  });
  const [user, setUser] = useState(null); // ProfileOut
  const [loading, setLoading] = useState(Boolean(token));
  const [error, setError] = useState(null);

  // загрузка профиля по токену
  useEffect(() => {
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);

    fetch("/api/v1/me/profile", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (resp) => {
        if (!resp.ok) {
          const data = await resp.json().catch(() => ({}));
          const msg = data.detail || "Не удалось загрузить профиль";
          throw new Error(msg);
        }
        return resp.json();
      })
      .then((data) => {
        if (cancelled) return;
        setUser(data); // data: ProfileOut { id, email, role, full_name, phone }
        setError(null);
      })
      .catch((err) => {
        if (cancelled) return;
        console.error("Auth: профиль не загрузился:", err);
        setError(err.message);
        setUser(null);
        setToken(null);
        localStorage.removeItem("auth_token");
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  // логин
  const login = async (email, password) => {
    setLoading(true);
    setError(null);

    const resp = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await resp.json().catch(() => ({}));

    if (!resp.ok) {
      const detail = data?.detail;
      const msg =
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
            ? detail.map((e) => e?.msg).filter(Boolean).join("; ")
            : "Неверный email или пароль";

      setLoading(false); // важно, чтобы не зависло
      throw new Error(msg);
    }

    const newToken = data.access_token;
    setToken(newToken);
    localStorage.setItem("auth_token", newToken);

    // loading выключится в useEffect.finally после /me/profile
    return newToken;
  };


  const logout = () => {
    setToken(null);
    setUser(null);
    setError(null);
    localStorage.removeItem("auth_token");
  };

  // обновление профиля (full_name / phone / пароль)
  const updateProfile = async (payload) => {
    if (!token) {
      throw new Error("Не авторизован");
    }

    const resp = await fetch("/api/v1/me/profile", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      const data = await resp.json().catch(() => ({}));
      const msg = data.detail || "Не удалось обновить профиль";
      throw new Error(msg);
    }

    const data = await resp.json(); // обновлённый ProfileOut
    setUser(data);
    return data;
  };

  const value = {
    token,
    user,
    loading,
    error,
    login,
    logout,
    updateProfile,
  };

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth должен вызываться внутри <AuthProvider>");
  }
  return ctx;
}
