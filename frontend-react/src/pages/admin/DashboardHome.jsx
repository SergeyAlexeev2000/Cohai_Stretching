// src/pages/admin/DashboardHome.jsx
import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext.jsx";
import { adminRequest } from "../../api/adminRequest.js";

function StatCard({ title, value, hint }) {
  return (
    <div className="rounded-xl border border-neutral-800 bg-neutral-950/40 p-4">
      <div className="text-sm text-neutral-400">{title}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
      {hint && <div className="mt-2 text-xs text-neutral-500">{hint}</div>}
    </div>
  );
}

function ActionButton({ title, subtitle, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full rounded-xl border border-neutral-800 bg-neutral-950/40 p-4 text-left hover:border-pink-500 transition-colors"
    >
      <div className="text-sm font-medium">{title}</div>
      {subtitle && <div className="mt-1 text-xs text-neutral-500">{subtitle}</div>}
    </button>
  );
}

export default function DashboardHome() {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [leads, setLeads] = useState([]);
  const [locations, setLocations] = useState([]);
  const [plans, setPlans] = useState([]);
  const [sessions, setSessions] = useState([]);

  const stats = useMemo(() => {
    const totalLeads = Array.isArray(leads) ? leads.length : 0;
    const unprocessedLeads = Array.isArray(leads)
      ? leads.filter((x) => x && x.is_processed === false).length
      : 0;

    const locationsCount = Array.isArray(locations) ? locations.length : 0;
    const plansCount = Array.isArray(plans) ? plans.length : 0;

    const activeSessions = Array.isArray(sessions)
      ? sessions.filter((s) => s && s.is_active !== false).length
      : 0;

    return {
      totalLeads,
      unprocessedLeads,
      locationsCount,
      plansCount,
      activeSessions,
    };
  }, [leads, locations, plans, sessions]);

  const load = async () => {
    if (!token) return;

    setLoading(true);
    setError(null);
    try {
      const [leadsData, locationsData, plansData, sessionsData] = await Promise.all([
        adminRequest("/admin/leads", { token, method: "GET" }),
        adminRequest("/admin/locations", { token, method: "GET" }),
        adminRequest("/admin/memberships", { token, method: "GET" }),
        adminRequest("/admin/class-sessions", { token, method: "GET" }),
      ]);

      setLeads(Array.isArray(leadsData) ? leadsData : leadsData?.items ?? []);
      setLocations(Array.isArray(locationsData) ? locationsData : locationsData?.items ?? []);
      setPlans(Array.isArray(plansData) ? plansData : plansData?.items ?? []);
      setSessions(Array.isArray(sessionsData) ? sessionsData : sessionsData?.items ?? []);
    } catch (e) {
      setError(e?.message || "Не удалось загрузить данные обзора");
      setLeads([]);
      setLocations([]);
      setPlans([]);
      setSessions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Обзор</h1>
          <p className="text-sm text-neutral-400">
            Сводка по студии + быстрые действия.
          </p>
          {user?.role && (
            <div className="mt-1 text-xs text-neutral-500">
              Роль: {user.role}
            </div>
          )}
        </div>

        <button
          onClick={load}
          className="rounded-md border border-neutral-700 px-3 py-2 text-sm hover:border-pink-500"
          disabled={loading}
        >
          {loading ? "Обновляю..." : "Обновить"}
        </button>
      </div>

      {error && (
        <div className="text-sm text-red-400 wrap-break-word">
          Ошибка: {error}
        </div>
      )}

      {/* Карточки со сводкой */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <StatCard
          title="Заявки"
          value={stats.totalLeads}
          hint={`Необработано: ${stats.unprocessedLeads}`}
        />
        <StatCard title="Локации" value={stats.locationsCount} />
        <StatCard title="Тарифы" value={stats.plansCount} />
        <StatCard title="Занятия (активные)" value={stats.activeSessions} />
      </div>

      {/* Быстрые действия */}
      <div className="rounded-xl border border-neutral-800 bg-neutral-950/40 p-4">
        <div className="text-sm font-medium mb-3">Быстрые действия</div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <ActionButton
            title="Заявки"
            subtitle="Открыть список и отметить обработанные"
            onClick={() => navigate("/admin/leads")}
          />
          <ActionButton
            title="Локации"
            subtitle="Список, создание, редактирование, удаление"
            onClick={() => navigate("/admin/locations")}
          />
          <ActionButton
            title="Абонементы (тарифы)"
            subtitle="Список + создание + правка названия (A)"
            onClick={() => navigate("/admin/memberships")}
          />
          <ActionButton
            title="Расписание"
            subtitle="Список class sessions + фильтры (A)"
            onClick={() => navigate("/admin/classes")}
          />
        </div>
      </div>

      {/* Небольшой блок “подсказка” */}
      <div className="text-xs text-neutral-600">
        Следующий шаг: добавим модалки/формы прямо отсюда (например “Создать локацию/тариф/занятие”).
      </div>
    </div>
  );
}

