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

function formatTime(timeStr) {
  if (!timeStr) return "";
  // timeStr вида "18:30:00"
  const [h, m] = timeStr.split(":");
  if (h === undefined || m === undefined) return timeStr;
  return `${h}:${m}`;
}

function statusLabel(status) {
  switch (status) {
    case "PLANNED":
      return "Запланировано";
    case "ATTENDED":
      return "Посетил";
    case "MISSED":
      return "Не пришёл";
    case "CANCELED":
      return "Отменено";
    default:
      return status;
  }
}

function statusClass(status) {
  switch (status) {
    case "PLANNED":
      return "badge badge--blue";
    case "ATTENDED":
      return "badge badge--green";
    case "MISSED":
      return "badge badge--red";
    case "CANCELED":
      return "badge badge--gray";
    default:
      return "badge";
  }
}

function ClassItem({ item, onCancel, cancelling }) {
  const canCancel = item.status === "PLANNED";

  return (
    <div className="class-item">
      <div className="class-item__main">
        <div>
          <div className="class-item__date">
            {formatDate(item.class_date)} ·{" "}
            {formatTime(item.start_time)}–{formatTime(item.end_time)}
          </div>
          <div className="class-item__sub">
            Запись №{item.attendance_id} · Класс #{item.class_session_id}
          </div>
        </div>
        <span className={statusClass(item.status)}>
          {statusLabel(item.status)}
        </span>
      </div>

      <div className="class-item__footer">
        {canCancel ? (
          <button
            type="button"
            className="class-item__cancel-btn"
            onClick={() => onCancel(item.attendance_id)}
            disabled={cancelling}
          >
            {cancelling ? "Отменяем..." : "Отменить запись"}
          </button>
        ) : (
          <span className="class-item__note">
            Отмена недоступна для этого занятия.
          </span>
        )}
      </div>
    </div>
  );
}

export default function ClientClassesPage() {
  const { token } = useAuth();
  const [data, setData] = useState({ upcoming: [], history: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cancellingId, setCancellingId] = useState(null);

  const loadData = () => {
    if (!token) return;
    setLoading(true);
    setError(null);

    fetch("/api/v1/me/classes", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (resp) => {
        if (!resp.ok) {
          const body = await resp.json().catch(() => ({}));
          const msg = body.detail || "Не удалось загрузить занятия.";
          throw new Error(msg);
        }
        return resp.json();
      })
      .then((json) => {
        setData(json);
      })
      .catch((err) => {
        console.error("Ошибка загрузки занятий:", err);
        setError(err.message || "Ошибка загрузки занятий.");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, [token]);

  const handleCancel = async (attendanceId) => {
    if (!token) return;
    setCancellingId(attendanceId);

    try {
      const resp = await fetch("/api/v1/me/classes/cancel", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ attendance_id: attendanceId }),
      });

      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        const msg = body.detail || "Не удалось отменить запись.";
        throw new Error(msg);
      }

      // можно было бы обновить по месту, но надёжнее просто перезагрузить список
      await resp.json(); // нам не так важен ответ, главное — успех
      loadData();
    } catch (err) {
      console.error("Ошибка отмены занятия:", err);
      alert(err.message || "Ошибка при отмене занятия.");
    } finally {
      setCancellingId(null);
    }
  };

  if (loading) {
    return (
      <div className="client-dashboard-card">
        Загрузка списка занятий...
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

  const { upcoming, history } = data;

  return (
    <div className="space-y-8">
      <div className="client-dashboard-card">
        <h2 className="text-lg font-semibold mb-2">Ближайшие занятия</h2>
        <p className="text-sm text-neutral-500 mb-4">
          Занятия, на которые вы записаны. Можно отменить, если не
          планируете приходить.
        </p>

        {upcoming.length === 0 && (
          <div className="text-sm text-neutral-600">
            У вас пока нет записей на ближайшие занятия.
          </div>
        )}

        {upcoming.map((item) => (
          <ClassItem
            key={item.attendance_id}
            item={item}
            onCancel={handleCancel}
            cancelling={cancellingId === item.attendance_id}
          />
        ))}
      </div>

      <div className="client-dashboard-card">
        <h2 className="text-lg font-semibold mb-2">История занятий</h2>
        <p className="text-sm text-neutral-500 mb-4">
          Посещённые, пропущенные и отменённые занятия.
        </p>

        {history.length === 0 && (
          <div className="text-sm text-neutral-600">
            История занятий пока пуста.
          </div>
        )}

        {history.map((item) => (
          <ClassItem
            key={item.attendance_id}
            item={item}
            onCancel={handleCancel}
            cancelling={cancellingId === item.attendance_id}
          />
        ))}
      </div>
    </div>
  );
}
