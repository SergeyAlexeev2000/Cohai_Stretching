import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";

function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function statusLabel(status) {
  switch (status) {
    case "ACTIVE":
      return "Активен";
    case "EXPIRED":
      return "Истёк";
    case "FROZEN":
      return "Заморожен";
    case "CANCELED":
      return "Отменён";
    default:
      return status;
  }
}

function statusClass(status) {
  switch (status) {
    case "ACTIVE":
      return "badge badge--green";
    case "EXPIRED":
      return "badge badge--gray";
    case "FROZEN":
      return "badge badge--blue";
    case "CANCELED":
      return "badge badge--red";
    default:
      return "badge";
  }
}

function MembershipCard({ m }) {
  const hasLimit = m.visits_total !== null && m.visits_total !== undefined;
  const remaining = hasLimit ? m.visits_total - m.visits_used : null;

  return (
    <div className="membership-card">
      <div className="membership-card__header">
        <div>
          <div className="membership-card__title">
            Тариф #{m.membership_plan_id}
          </div>
          <div className="membership-card__dates">
            {formatDate(m.start_date)} — {formatDate(m.end_date)}
          </div>
        </div>
        <span className={statusClass(m.status)}>
          {statusLabel(m.status)}
        </span>
      </div>

      <div className="membership-card__body">
        <div className="membership-card__row">
          <span>Начало действия</span>
          <span>{formatDate(m.start_date)}</span>
        </div>
        <div className="membership-card__row">
          <span>Окончание</span>
          <span>{formatDate(m.end_date)}</span>
        </div>

        {hasLimit && (
          <>
            <div className="membership-card__row">
              <span>Всего занятий</span>
              <span>{m.visits_total}</span>
            </div>
            <div className="membership-card__row">
              <span>Использовано</span>
              <span>{m.visits_used}</span>
            </div>
            <div className="membership-card__row">
              <span>Осталось</span>
              <span>{remaining}</span>
            </div>
          </>
        )}

        {!hasLimit && (
          <div className="membership-card__row">
            <span>Посещения</span>
            <span>Без ограничения (по времени)</span>
          </div>
        )}

        <div className="membership-card__row membership-card__row--muted">
          <span>Оформлен</span>
          <span>{formatDate(m.created_at)}</span>
        </div>
      </div>
    </div>
  );
}

export default function ClientMembershipsPage() {
  const { token } = useAuth();
  const [data, setData] = useState({ active: [], history: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!token) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetch("/api/v1/me/memberships", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (resp) => {
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({}));
          const msg = body.detail || "Не удалось загрузить абонементы.";
          throw new Error(msg);
        }
        return resp.json();
      })
      .then((json) => {
        if (cancelled) return;
        setData(json);
      })
      .catch((err) => {
        if (cancelled) return;
        console.error("Ошибка загрузки абонементов:", err);
        setError(err.message || "Ошибка загрузки абонементов.");
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  if (loading) {
    return (
      <div className="client-dashboard-card">
        Загрузка абонементов...
      </div>
    );
  }

  if (error) {
    return (
      <div className="client-dashboard-card">
        <div className="text-red-600 text-sm mb-2">
          {error}
        </div>
        <div className="text-sm text-neutral-600">
          Попробуйте обновить страницу. Если проблема сохраняется —
          напишите администратору.
        </div>
      </div>
    );
  }

  const { active, history } = data;

  return (
    <div className="space-y-8">
      <div className="client-dashboard-card">
        <h2 className="text-lg font-semibold mb-2">Активные абонементы</h2>
        <p className="text-sm text-neutral-500 mb-4">
          Здесь отображаются абонементы, по которым вы сейчас можете ходить
          на занятия.
        </p>

        {active.length === 0 && (
          <div className="text-sm text-neutral-600">
            У вас нет активных абонементов.
          </div>
        )}

        {active.map((m) => (
          <MembershipCard key={m.id} m={m} />
        ))}
      </div>

      <div className="client-dashboard-card">
        <h2 className="text-lg font-semibold mb-2">История абонементов</h2>
        <p className="text-sm text-neutral-500 mb-4">
          Завершённые, истёкшие, замороженные или отменённые абонементы.
        </p>

        {history.length === 0 && (
          <div className="text-sm text-neutral-600">
            История абонементов пока пуста.
          </div>
        )}

        {history.map((m) => (
          <MembershipCard key={m.id} m={m} />
        ))}
      </div>
    </div>
  );
}
