import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";
import { Link } from "react-router-dom";

export default function ClientDashboardHome() {
  const { token } = useAuth();

  const [nextClass, setNextClass] = useState(null);
  const [membership, setMembership] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;

    async function loadAll() {
      setLoading(true);
      try {
        // 1. Load classes
        const cResp = await fetch("/api/v1/me/classes", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (cResp.ok) {
          const cJson = await cResp.json();
          const next = cJson.upcoming?.[0] || null;
          setNextClass(next);
        }

        // 2. Load memberships
        const mResp = await fetch("/api/v1/me/memberships", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (mResp.ok) {
          const mJson = await mResp.json();
          const active = mJson.active?.[0] || null;
          setMembership(active);
        }
      } catch (err) {
        console.error("Dashboard load error:", err);
      } finally {
        setLoading(false);
      }
    }

    loadAll();
  }, [token]);

  if (loading) {
    return (
      <div className="client-dashboard-card">
        Загружаем данные...
      </div>
    );
  }

  return (
    <div className="space-y-6">

      {/* 1. Приветствие */}
      <div className="client-dashboard-card">
        <h2 className="text-lg font-semibold">Обзор</h2>
        <p className="text-sm text-neutral-500">
          Добро пожаловать! Здесь показана ваша ближайшая активность.
        </p>
      </div>

      {/* 2. Ближайшее занятие */}
      <div className="client-dashboard-card">
        <h3 className="font-semibold mb-2">Ближайшее занятие</h3>

        {nextClass ? (
          <div className="text-sm space-y-1">
            <p><b>Дата:</b> {nextClass.class_date}</p>
            <p>
              <b>Время:</b> {nextClass.start_time.slice(0,5)}–
              {nextClass.end_time.slice(0,5)}
            </p>
            <p><b>Статус:</b> {nextClass.status}</p>
            <Link
              to="/client/classes"
              className="text-pink-500 text-sm underline"
            >
              Перейти к занятиям →
            </Link>
          </div>
        ) : (
          <p className="text-sm text-neutral-600">
            У вас нет запланированных занятий.
          </p>
        )}
      </div>

      {/* 3. Активный абонемент */}
      <div className="client-dashboard-card">
        <h3 className="font-semibold mb-2">Активный абонемент</h3>

        {membership ? (
          <div className="text-sm space-y-1">
            <p><b>Название:</b> {membership.name || `#${membership.id}`}</p>
            {membership.expires_at && (
              <p><b>Действует до:</b> {membership.expires_at}</p>
            )}
            <Link
              to="/client/memberships"
              className="text-pink-500 text-sm underline"
            >
              Все абонементы →
            </Link>
          </div>
        ) : (
          <p className="text-sm text-neutral-600">
            У вас нет активных абонементов.
          </p>
        )}
      </div>

      {/* 4. Быстрые действия */}
      <div className="client-dashboard-card">
        <h3 className="font-semibold mb-3">Быстрые действия</h3>

        <div className="grid grid-cols-2 gap-3 text-sm">
          <Link to="/client/schedule" className="quick-link">
            📅 Моё расписание
          </Link>
          <Link to="/client/classes" className="quick-link">
            🧘 Мои занятия
          </Link>
          <Link to="/client/memberships" className="quick-link">
            🎫 Абонементы
          </Link>
          <Link to="/client/profile" className="quick-link">
            ⚙ Профиль
          </Link>
        </div>
      </div>
    </div>
  );
}
