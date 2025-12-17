// src/pages/admin/AdminDashboardLayout.jsx
import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../../context/AuthContext.jsx";

function AdminNavLink({ to, children }) {
  return (
    <NavLink
      to={to}
      end
      className={({ isActive }) =>
        [
          "px-3 py-2 rounded-md text-sm font-medium",
          "transition-colors duration-150",
          isActive
            ? "bg-pink-600/20 text-pink-400 border border-pink-500/40"
            : "text-neutral-300 hover:bg-neutral-800 hover:text-white",
        ].join(" ")
      }
    >
      {children}
    </NavLink>
  );
}

export default function AdminDashboardLayout() {
  const { user, logout } = useAuth();

  const displayName = user?.full_name || user?.email || "Администратор";

  return (
    <div className="min-h-screen bg-neutral-900 text-white flex">
      {/* Сайдбар */}
      <aside className="w-64 border-r border-neutral-800 flex flex-col">
        <div className="px-4 py-4 border-b border-neutral-800">
          <div className="text-xs uppercase tracking-wide text-neutral-500 mb-1">
            Панель администратора
          </div>
          <div className="font-semibold text-sm">{displayName}</div>
          <div className="text-xs text-neutral-500 mt-0.5">
            Роль: {user?.role}
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 flex flex-col gap-1 text-sm">
          <AdminNavLink to="/admin">Обзор</AdminNavLink>
          <AdminNavLink to="/admin/leads">Заявки</AdminNavLink>
          <AdminNavLink to="/admin/locations">Локации</AdminNavLink>
          <AdminNavLink to="/admin/memberships">Абонементы</AdminNavLink>
          <AdminNavLink to="/admin/classes">Расписание</AdminNavLink>
        </nav>

        <div className="px-4 py-4 border-t border-neutral-800">
          <button
            type="button"
            onClick={logout}
            className="w-full text-sm px-3 py-2 rounded-md border border-neutral-700 hover:border-pink-500 hover:text-pink-400 transition-colors"
          >
            Выйти
          </button>
        </div>
      </aside>

      {/* Контент */}
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}
