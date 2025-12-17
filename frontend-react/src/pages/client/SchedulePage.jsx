import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";

function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString("ru-RU", {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
  });
}

function formatTime(timeStr) {
  if (!timeStr) return "";
  const [h, m] = timeStr.split(":");
  if (h === undefined || m === undefined) return timeStr;
  return `${h}:${m}`;
}

function CalendarClassCard({ cls }) {
  const title =
    cls.program_title ||
    cls.program_name ||
    (cls.program_type_id
      ? `Программа #${cls.program_type_id}`
      : "Занятие");

  const location =
    cls.location_name ||
    cls.location_title ||
    (cls.location_id ? `Локация #${cls.location_id}` : null);

  const trainer =
    cls.trainer_name ||
    (cls.trainer_id ? `Тренер #${cls.trainer_id}` : null);

  const isBooked = cls.is_booked ?? false;
  const status = cls.attendance_status || cls.status || null;

  return (
    <div className="calendar-class">
      <div className="calendar-class__main">
        <div>
          <div className="calendar-class__time">
            {formatTime(cls.start_time)}–{formatTime(cls.end_time)}
          </div>
          <div className="calendar-class__title">{title}</div>
          {location && (
            <div className="calendar-class__meta">📍 {location}</div>
          )}
          {trainer && (
            <div className="calendar-class__meta">👤 {trainer}</div>
          )}
        </div>

        <div className="calendar-class__tags">
          {isBooked && <span className="badge badge--blue">Вы записаны</span>}
          {status && !isBooked && (
            <span className="badge badge--gray">{status}</span>
          )}
        </div>
      </div>
    </div>
  );
}

function CalendarDay({ day }) {
  const dateValue = day.date || day.day || day.class_date;
  return (
    <div className="calendar-day">
      <div className="calendar-day__header">
        <span className="calendar-day__date">
          {formatDate(dateValue)}
        </span>
        <span className="calendar-day__count">
          {day.classes?.length || 0} зан.
        </span>
      </div>

      {(!day.classes || day.classes.length === 0) && (
        <div className="calendar-day__empty">
          В этот день нет занятий.
        </div>
      )}

      {day.classes?.map((cls, idx) => (
        <CalendarClassCard
          key={cls.id || cls.class_session_id || `${idx}-${cls.start_time}`}
          cls={cls}
        />
      ))}
    </div>
  );
}

export default function ClientSchedulePage() {
  const { token } = useAuth();
  const [days, setDays] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!token) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    // диапазон дат: сегодня + 14 дней
    const today = new Date();
    const startDate = today.toISOString().slice(0, 10); // YYYY-MM-DD

    const end = new Date(today);
    end.setDate(end.getDate() + 14);
    const endDate = end.toISOString().slice(0, 10);

    const url = `/api/v1/me/calendar?start_date=${startDate}&end_date=${endDate}`;

    fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (resp) => {
        if (!resp.ok) {
          let msg = "Не удалось загрузить расписание.";
          try {
            const body = await resp.json();
            if (typeof body.detail === "string") {
              msg = body.detail;
            } else if (Array.isArray(body.detail)) {
              msg = body.detail
                .map((d) => d.msg || JSON.stringify(d))
                .join("; ");
            }
          } catch (_) {
            // ignore
          }
          throw new Error(msg);
        }
        return resp.json();
      })
      .then((json) => {
        if (cancelled) return;
        if (Array.isArray(json.days)) {
          setDays(json.days);
        } else if (Array.isArray(json)) {
          setDays(json);
        } else {
          setDays([]);
        }
      })
      .catch((err) => {
        if (cancelled) return;
        console.error("Ошибка загрузки календаря:", err);
        setError(err.message || "Ошибка загрузки расписания.");
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
        Загрузка расписания...
      </div>
    );
  }

  if (error) {
    return (
      <div className="client-dashboard-card">
        <div className="text-red-600 text-sm mb-2">{error}</div>
        <div className="text-sm text-neutral-600">
          Попробуйте обновить страницу. Если проблема сохраняется —
          напишите администратору.
        </div>
      </div>
    );
  }

  if (!days || days.length === 0) {
    return (
      <div className="client-dashboard-card">
        <h2 className="text-lg font-semibold mb-2">Моё расписание</h2>
        <p className="text-sm text-neutral-500 mb-2">
          В выбранном периоде нет занятий.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="client-dashboard-card">
        <h2 className="text-lg font-semibold mb-2">Моё расписание</h2>
        <p className="text-sm text-neutral-500">
          Показаны занятия на ближайшие две недели.
        </p>
      </div>

      {days.map((day, idx) => (
        <CalendarDay key={day.date || day.day || idx} day={day} />
      ))}
    </div>
  );
}
