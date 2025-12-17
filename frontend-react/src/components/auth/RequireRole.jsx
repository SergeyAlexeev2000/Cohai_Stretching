// src/components/auth/RequireRole.jsx
import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext.jsx";

export default function RequireRole({ allowedRoles, children }) {
  const { token, user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div>Загрузка...</div>;
  }

  // не авторизован вообще → на /login
  if (!token || !user) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location }}
      />
    );
  }

  // роль не подходит → можно просто на главную
  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
}
