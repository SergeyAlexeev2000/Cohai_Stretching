// src/components/auth/RequireAuth.jsx
import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext.jsx";

export default function RequireAuth({ children }) {
  const { token, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div>Загрузка...</div>;
  }

  if (!token) {
    // пока редиректим на главную; позже можно сделать /login
    return <Navigate to="/" replace state={{ from: location }} />;
  }

  return children;
}
