import React from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext.jsx";
import "./client-dashboard/layout.css";
import "./client-dashboard/common.css";
import "./client-dashboard/memberships.css";
import "./client-dashboard/classes.css";
import "./client-dashboard/calendar.css";
import "./client-dashboard/leads.css";


const navItems = [
  { to: "/client", label: "Обзор", end: true },
  { to: "/client/schedule", label: "Расписание" },
  { to: "/client/classes", label: "Мои занятия" },
  { to: "/client/memberships", label: "Абонементы" },
  { to: "/client/profile", label: "Профиль" },
  { to: "/client/leads", label: "Мои заявки" },
];

export default function ClientDashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/"); // после выхода отправляем на главную
  };

  return (
    <div className="client-dashboard">
      <aside className="client-dashboard__sidebar">
        <div className="client-dashboard__brand">Cohai Stretching</div>

        <nav className="client-dashboard__nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                "client-dashboard__nav-link" +
                (isActive ? " client-dashboard__nav-link--active" : "")
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="client-dashboard__main">
        <header className="client-dashboard__header">
          <div className="client-dashboard__header-inner">
            <h1 className="client-dashboard__title">
              Личный кабинет клиента
            </h1>
            <div className="client-dashboard__user">
              {user && (
                <span className="client-dashboard__user-email">
                  {user.full_name || user.email}
                </span>
              )}
              <button
                type="button"
                className="client-dashboard__logout-btn"
                onClick={handleLogout}
              >
                Выйти
              </button>
            </div>
          </div>
        </header>

        <main className="client-dashboard__content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
