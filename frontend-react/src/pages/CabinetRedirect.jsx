// src/pages/CabinetRedirect.jsx
import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function CabinetRedirect() {
  const { token, user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <div className="p-6 text-neutral-300">Загрузка...</div>;

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  // token есть, но user ещё нет — НЕ ПИХАЕМ на /login, просто ждём профиль
  if (!user) {
    return <div className="p-6 text-neutral-300">Загрузка профиля...</div>;
  }

  if (user.role === "SUPERADMIN" || user.role === "ADMIN") {
    return <Navigate to="/admin" replace />;
  }

  if (user.role === "TRAINER") {
    return <Navigate to="/trainer" replace />;
  }
  
  return <Navigate to="/client" replace />;
}
